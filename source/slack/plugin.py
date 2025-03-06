#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import json
import requests

from unmanic.libs.unplugins.settings import PluginSettings

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.slack")


class Settings(PluginSettings):
    settings = {
        "webhook_url": "",
        "channel": "",
        "username": "Unmanic",
        "icon_emoji": ":robot_face:",
        "notify_on_file_movement": True,
        "notify_on_task_completion": True,
        "notify_on_file_test": True,
        "notify_on_worker_process": True,
        "create_synology_public_links": False,
        "synology_url": "http://your-synology-ip:5000",
        "synology_username": "",
        "synology_password": "",
        "synology_link_expiry": "0",  # 0 means never expire
    }

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)


def create_synology_public_link(file_path, settings):
    """
    Create a public link for a file on Synology NAS
    
    :param file_path: The path to the file on the Synology NAS
    :param settings: The plugin settings
    :return: The public link URL or None if failed
    """
    if not settings.get_setting('create_synology_public_links'):
        return None
        
    syno_url = settings.get_setting('synology_url')
    username = settings.get_setting('synology_username')
    password = settings.get_setting('synology_password')
    
    if not syno_url or not username or not password:
        logger.error("Synology credentials not properly configured")
        return None
    
    try:
        # Step 1: Authenticate
        login_url = f"{syno_url}/webapi/auth.cgi"
        login_params = {
            "api": "SYNO.API.Auth",
            "version": "6",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": "FileStation",
            "format": "sid"
        }
        
        login_res = requests.get(login_url, params=login_params).json()
        if not login_res.get("success", False):
            logger.error(f"Failed to authenticate with Synology: {login_res.get('error', {}).get('code', 'Unknown error')}")
            return None
            
        sid = login_res["data"]["sid"]
        
        # Step 2: Create a public link
        share_url = f"{syno_url}/webapi/entry.cgi"
        share_params = {
            "api": "SYNO.FileStation.Sharing",
            "version": "3",
            "method": "create",
            "path": file_path,
            "password": "",
            "expire_time": settings.get_setting('synology_link_expiry'),
            "_sid": sid
        }
        
        share_res = requests.get(share_url, params=share_params).json()
        if not share_res.get("success", False):
            logger.error(f"Failed to create Synology public link: {share_res.get('error', {}).get('code', 'Unknown error')}")
            return None
            
        public_link = share_res["data"]["links"][0]["url"]
        
        # Step 3: Logout
        logout_url = f"{syno_url}/webapi/auth.cgi"
        logout_params = {
            "api": "SYNO.API.Auth",
            "version": "6",
            "method": "logout",
            "session": "FileStation",
            "_sid": sid
        }
        
        requests.get(logout_url, params=logout_params)
        
        return public_link
        
    except Exception as e:
        logger.error(f"Error creating Synology public link: {str(e)}")
        return None


def send_slack_notification(webhook_url, message, channel=None, username=None, icon_emoji=None):
    """
    Send a notification to Slack
    
    :param webhook_url: The Slack webhook URL
    :param message: The message to send
    :param channel: The channel to send the message to
    :param username: The username to use for the message
    :param icon_emoji: The emoji to use as the icon
    :return: 
    """
    if not webhook_url:
        logger.error("Slack webhook URL not configured")
        return False

    payload = {
        "text": message,
    }
    
    if channel:
        payload["channel"] = channel
    if username:
        payload["username"] = username
    if icon_emoji:
        payload["icon_emoji"] = icon_emoji
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send Slack notification: {response.text}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error sending Slack notification: {str(e)}")
        return False


def on_library_management_file_test(data):
    """
    Runner function - enables the plugin to test if a file should be added to the library's processing queue.
    
    The 'data' object argument includes:
        path                            - String containing the full path to the file being tested.
        issues                          - List of currently found issues with the file.
        add_file_to_pending_tasks       - Boolean, is the file currently marked to be added to the queue for processing.
        library_id                      - The library that the file belongs to.
        is_video                        - Boolean, is the file a video file.
        is_audio                        - Boolean, is the file an audio file.

    :param data:
    :return:
    
    """
    # Get settings
    settings = Settings(library_id=data.get('library_id'))
    
    # Check if notifications for file tests are enabled
    if not settings.get_setting('notify_on_file_test'):
        return
    
    # Get webhook URL
    webhook_url = settings.get_setting('webhook_url')
    if not webhook_url:
        logger.error("Slack webhook URL not configured")
        return
    
    # Get file path
    file_path = data.get('path', '')
    
    # Create message
    message = f"*File Test*\nFile: `{file_path}`"
    
    # Add info about file type
    if data.get('is_video', False):
        message += "\nType: Video"
    elif data.get('is_audio', False):
        message += "\nType: Audio"
    else:
        message += "\nType: Other"
    
    # Add info about issues
    issues = data.get('issues', [])
    if issues:
        message += "\nIssues:"
        for issue in issues:
            message += f"\n- {issue}"
    
    # Add info about whether file will be processed
    if data.get('add_file_to_pending_tasks', False):
        message += "\nStatus: ✅ File will be added to processing queue"
    else:
        message += "\nStatus: 🔥 File will not be processed"
    
    # Send notification
    send_slack_notification(
        webhook_url=webhook_url,
        message=message,
        channel=settings.get_setting('channel'),
        username=settings.get_setting('username'),
        icon_emoji=settings.get_setting('icon_emoji')
    )
    
    return


def on_worker_process(data):
    """
    Runner function - enables the plugin to perform some processing on the file.
    
    The 'data' object argument includes:
        exec_command            - A command that Unmanic should execute. Can be empty.
        command_progress_parser - A function that Unmanic can use to parse the STDOUT of the command to collect progress stats. Can be empty.
        file_in                 - The source file to be processed by the command.
        file_out                - The destination that the command should output (may be the same as the file_in if necessary).
        original_file_path      - The absolute path to the original file.
        repeat                  - Boolean, should this runner be executed again once completed with the same variables.
        library_id              - The library that the file belongs to.

    :param data:
    :return:
    
    """
    # Get settings
    settings = Settings(library_id=data.get('library_id'))
    
    # Check if notifications for worker processes are enabled
    if not settings.get_setting('notify_on_worker_process'):
        return
    
    # Get webhook URL
    webhook_url = settings.get_setting('webhook_url')
    if not webhook_url:
        logger.error("Slack webhook URL not configured")
        return
    
    # Get file info
    file_in = data.get('file_in', '')
    file_out = data.get('file_out', '')
    original_file_path = data.get('original_file_path', '')
    
    # Create message
    message = f"🏃 *Conversion Started*\nOriginal File: `{original_file_path}`"
    
    # Add info about processing
    if file_in != original_file_path:
        message += f"\nProcessing: `{file_in}`"
    
    # if file_out != file_in:
    #     message += f"\nOutput: `{file_out}`"
    
    # Add info about command if present
    exec_command = data.get('exec_command', [])
    if exec_command:
        message += f"\nCommand: `{' '.join(exec_command)}`"
    
    # Send notification
    send_slack_notification(
        webhook_url=webhook_url,
        message=message,
        channel=settings.get_setting('channel'),
        username=settings.get_setting('username'),
        icon_emoji=settings.get_setting('icon_emoji')
    )
    
    return


def on_postprocessor_file_movement(data):
    """
    Runner function - provides a means for additional postprocessor functions based on the file movement.

    The 'data' object argument includes:
        source_data             - Dictionary containing data pertaining to the original source file.
        copy_data               - Dictionary containing data pertaining to the copied file.
        move_data               - Dictionary containing data pertaining to the moved file.
        file_move_processes_success - Boolean, did all postprocessor movement tasks complete successfully.

    :param data:
    :return:
    
    """
    # Get settings
    settings = Settings(library_id=data.get('library_id'))
    
    # Check if notifications for file movements are enabled
    if not settings.get_setting('notify_on_file_movement'):
        return

    # Get webhook URL
    webhook_url = settings.get_setting('webhook_url')
    if not webhook_url:
        logger.error("Slack webhook URL not configured")
        return

    # Get source file info
    source_data = data.get('source_data', {})
    source_path = source_data.get('abspath', '')
    
    # Get move data
    move_data = data.get('move_data', {})
    move_path = move_data.get('abspath', '') if move_data else ''
    
    # Get copy data
    copy_data = data.get('copy_data', {})
    copy_path = copy_data.get('abspath', '') if copy_data else ''
    
    # Check if file was moved or copied
    if move_path:
        message = f"*File Moved*\nFrom: `{source_path}`\nTo: `{move_path}`"
    elif copy_path:
        message = f"*File Copied*\nFrom: `{source_path}`\nTo: `{copy_path}`"
    else:
        # No file movement occurred
        return
    
    # Send notification
    send_slack_notification(
        webhook_url=webhook_url,
        message=message,
        channel=settings.get_setting('channel'),
        username=settings.get_setting('username'),
        icon_emoji=settings.get_setting('icon_emoji')
    )
    
    return


def on_postprocessor_task_results(data):
    """
    Runner function - provides a means for additional postprocessor functions based on the task success.

    The 'data' object argument includes:
        final_cache_path                - The path to the final cache file that was then used as the source for all destination files.
        library_id                      - The library that the current task is associated with.
        task_processing_success         - Boolean, did all task processes complete successfully.
        file_move_processes_success     - Boolean, did all postprocessor movement tasks complete successfully.
        destination_files               - List containing all file paths created by postprocessor file movements.
        source_data                     - Dictionary containing data pertaining to the original source file.

    :param data:
    :return:
    
    """
    # Get settings
    settings = Settings(library_id=data.get('library_id'))
    
    # Check if notifications for task completion are enabled
    if not settings.get_setting('notify_on_task_completion'):
        return

    # Get webhook URL
    webhook_url = settings.get_setting('webhook_url')
    if not webhook_url:
        logger.error("Slack webhook URL not configured")
        return
    
    # Get source file info
    source_data = data.get('source_data', {})
    source_path = source_data.get('abspath', '')
    
    # Get task status
    task_success = data.get('task_processing_success', False)
    move_success = data.get('file_move_processes_success', False)
    
    # Get destination files
    destination_files = data.get('destination_files', [])
    
    # Create message
    if task_success and move_success:
        status = "✅ *Video Successfully Converted*"
    else:
        status = "🔥 *Video Conversion Failed*"
    
    message = f"{status}\nSource: `{source_path}`"
    
    if destination_files:
        message += "\nOutput File:"
        
        # Check if Synology public links should be created
        create_links = settings.get_setting('create_synology_public_links')
        
        for dest_file in destination_files:
            message += f" `{dest_file}`"
            
            # Create and add Synology public link if enabled
            if create_links and task_success and move_success:
                public_link = create_synology_public_link(dest_file, settings)
                if public_link:
                    message += f" - <{public_link}|Download Link>"
    
    # Send notification
    send_slack_notification(
        webhook_url=webhook_url,
        message=message,
        channel=settings.get_setting('channel'),
        username=settings.get_setting('username'),
        icon_emoji=settings.get_setting('icon_emoji')
    )
    
    return
