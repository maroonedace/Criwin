import asyncio
from typing import Optional
from discord import app_commands, File, Interaction
from utils.audioclip import extract_youtube_url, validate_youtube_url, parse_ts, download_clip_mp3
from utils.index import send_message

active_downloads: set[int] = set()

# Command that converts a Youtube share link into an audio clip
def setup_audioclip(tree: app_commands.CommandTree):
    @tree.command(
        name="audioclip",
        description="Turns a YouTube share link into an mp3 audio clip (up to 5 minutes)."
    )
    @app_commands.describe(
        url="YouTube Share URL",
        length="Clip length (SS or MM:SS). Max 5m.",
        file_name="Optional custom file name"
    )
    async def audioclip(
        interaction: Interaction, 
        url: str, 
        length: Optional[str] = None, 
        file_name: Optional[str] = None
    ):
        # Get user id
        user_id = interaction.user.id

        # Limit to one downloads at a time per user
        if user_id in active_downloads:
            send_message(interaction, "⚠️ You already have a download in progress.")

        # Ensure that url matches the expected Youtube share URL structure
        try:
            validate_youtube_url(url)
        except ValueError as ve:
            send_message(interaction, f"❌ Invalid URL: {ve}")
         
        # Extract query parameters and video id
        video_id, start_time = extract_youtube_url(url)

        # Parse clip length
        try:
            provided_clip_length = parse_ts(length)
        except ValueError as ve:
            send_message(interaction, f"❌ Invalid time format: {ve}", )

        # Construct canonical URL
        canonical_url = f"https://www.youtube.com/watch?v={video_id}"

        # Defer response and add to active downloads
        await interaction.response.defer(ephemeral=True)
        active_downloads.add(user_id)

        try:
            # Download the clip in a separate thread
            mp3_path = await asyncio.to_thread(
                download_clip_mp3, 
                canonical_url, 
                start_time, 
                provided_clip_length, 
                file_name
            )

            # Send the file to the user
            await interaction.followup.send(
                file=File(str(mp3_path)), 
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Download failed: {str(e)}", 
                ephemeral=True
            )
        finally:
            # Cleanup: remove from active downloads and delete file
            active_downloads.discard(user_id)
            try:
                if 'mp3_path' in locals() and mp3_path.exists():
                    mp3_path.unlink(missing_ok=True)
            except Exception as e:
                print(f"[audioclip] cleanup failed: {e}")