Icon resource notes
-------------------

You can provide a custom icon for the Desktop shortcut by placing an
`.ico` file at `assets/task_manager.ico` in the project root. When you run
`.\install.ps1`, the installer will detect this file and use it for the
shortcut automatically.

If you don't provide an icon, the shortcut will use your Python executable's
icon by default.

How to create an .ico file from a PNG (one simple method):

1. Use an image editor or an online converter to convert a square PNG to
   a `.ico` file containing at least 16x16 and 256x256 sizes. Name it
   `task_manager.ico` and place it in the `assets/` directory.

2. Re-run `.\install.ps1` to recreate the Desktop shortcut with your icon.

Advanced: if you want a scripted conversion, you can use ImageMagick (if
installed):

```powershell
magick convert input.png -define icon:auto-resize=256,128,64,48,32,16 assets\task_manager.ico
```
