import io
from discord import File, Interaction
from PIL import Image


async def handle_image(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    
    background = Image.open("oh-this-is-beautiful.png").convert("RGBA")

    overlay = Image.open("20260104_110644.jpg").convert("RGBA")

    overlay = overlay.resize((151, 185))

    position = (438, 38)
     
    position2 = (438, 372)
    
    background.paste(overlay, position, overlay)
    
    background.paste(overlay, position2, overlay)
    
    buffer = io.BytesIO()
    background.save(buffer, format="PNG")
    buffer.seek(0)
    
    await interaction.followup.send(file=File(buffer, filename="result.png"), ephemeral=True)