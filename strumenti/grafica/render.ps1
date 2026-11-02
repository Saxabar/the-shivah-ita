# Render a word with GDI+ antialiasing and dump an 8-bit coverage mask.
# Output file: int32 width, int32 height, then width*height bytes (0 = paper, 255 = ink).
param(
    [string]$Text,
    [string]$Font = "Georgia",
    [single]$Size = 12,
    [switch]$Bold,
    [string]$Out
)
Add-Type -AssemblyName System.Drawing
$style = if ($Bold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }
$f = New-Object System.Drawing.Font($Font, $Size, $style, [System.Drawing.GraphicsUnit]::Pixel)
$bmp = New-Object System.Drawing.Bitmap(120, 32)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::White)
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$fmt = [System.Drawing.StringFormat]::GenericTypographic
$g.DrawString($Text, $f, [System.Drawing.Brushes]::Black, 4, 4, $fmt)
$g.Flush()
$w = $bmp.Width; $h = $bmp.Height
$bytes = New-Object byte[] (8 + $w * $h)
[BitConverter]::GetBytes([int]$w).CopyTo($bytes, 0)
[BitConverter]::GetBytes([int]$h).CopyTo($bytes, 4)
for ($y = 0; $y -lt $h; $y++) {
    for ($x = 0; $x -lt $w; $x++) {
        $c = $bmp.GetPixel($x, $y)
        $bytes[8 + $y * $w + $x] = [byte](255 - [int](($c.R + $c.G + $c.B) / 3))
    }
}
[System.IO.File]::WriteAllBytes($Out, $bytes)
