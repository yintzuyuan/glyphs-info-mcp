#!/usr/bin/env python3
"""
Installation Helper - Provides user-friendly module installation guidance

Provides clear installation steps and instructions when modules are not found.
"""


class InstallationHelper:
    """Module Installation Helper - Provides user-friendly installation messages"""

    # Module installation guidance messages
    INSTALLATION_MESSAGES = {
        "vanilla": """
❌ Vanilla module not found

Vanilla is the UI framework for Glyphs plugin development and needs to be installed separately.

📦 Installation methods:

Method 1️⃣: Via Glyphs Plugin Manager (Recommended)
  1. Open Glyphs.app
  2. Menu: Window > Plugin Manager
  3. Search for "vanilla"
  4. Click the Install button
  5. Restart Glyphs.app

Method 2️⃣: Install via Terminal
  pip3 install vanilla

📍 Expected installation location:
  ~/Library/Application Support/Glyphs 3/Repositories/vanilla

💡 Tips:
  - Restart Glyphs.app after installation
  - Ensure proper permissions for the Repositories folder
""",
        "drawBot": """
❌ DrawBot module not found

DrawBot is a Python drawing framework that can be used for Glyphs script development.

📦 Installation methods:

Method 1️⃣: Via Glyphs Plugin Manager
  1. Open Glyphs.app
  2. Menu: Window > Plugin Manager
  3. Search for "drawBot"
  4. Click the Install button

Method 2️⃣: Install via Terminal
  pip3 install drawBot

📍 Expected installation location:
  ~/Library/Application Support/Glyphs 3/Repositories/drawBot
""",
        "robofab": """
❌ RoboFab module not found

RoboFab is a Python library for font processing.

📦 Installation methods:

Install via Terminal:
  pip3 install robofab

Or search and install via Glyphs Plugin Manager
""",
        "mekkablue": r"""
❌ mekkablue scripts not found

The mekkablue script collection contains 358 production-ready Glyphs development scripts,
covering anchors, kerning, interpolation, paths, and all aspects of type design.

📦 Installation methods:

Method 1️⃣: Via Glyphs Plugin Manager (Recommended)
  1. Open Glyphs 3.app
  2. Menu: Window > Plugin Manager
  3. Switch to the Scripts tab
  4. Find "mekkablue scripts" and click Install
  5. Restart Glyphs 3.app (recommended)

Method 2️⃣: Manual installation via git
  cd ~/Library/Application\ Support/Glyphs\ 3/Repositories
  git clone https://github.com/mekkablue/Glyphs-Scripts.git mekkablue

📍 Expected installation location:
  ~/Library/Application Support/Glyphs 3/Repositories/mekkablue

🌐 Online resources:
  https://github.com/mekkablue/Glyphs-Scripts

💡 Tips:
  - Restart this MCP server after installation
  - Scripts will appear in Glyphs under Script > mekkablue menu
  - Update regularly to get the latest scripts
""",
    }

    # Generic installation message template
    GENERIC_MESSAGE_TEMPLATE = """
❌ Module '{module_name}' not found

📦 Recommended installation methods:

1️⃣  Via Glyphs Plugin Manager (Recommended)
   • Open Glyphs.app
   • Window > Plugin Manager
   • Search for "{module_name}"
   • Click Install

2️⃣  Install via Terminal
   pip3 install {module_name}

📍 Expected installation location:
   ~/Library/Application Support/Glyphs 3/Repositories/{module_name}

💡 Restart Glyphs.app after installation
"""

    @classmethod
    def get_installation_message(cls, module_name: str) -> str:
        """Get installation guidance message for a module

        Args:
            module_name: Module name (e.g., "vanilla", "drawBot")

        Returns:
            Formatted installation guidance message
        """
        # If predefined message exists, use predefined version
        if module_name in cls.INSTALLATION_MESSAGES:
            return cls.INSTALLATION_MESSAGES[module_name]

        # Otherwise use generic template
        return cls.GENERIC_MESSAGE_TEMPLATE.format(module_name=module_name)

    @classmethod
    def get_not_found_message(
        cls, module_name: str, query: str, available_items: list | None = None
    ) -> str:
        """Get suggestion message when query has no results

        Args:
            module_name: Module name
            query: User's query
            available_items: Available items list (optional)

        Returns:
            Formatted suggestion message
        """
        message = f"""
⚠️  No results found for '{query}' in {module_name}

Possible reasons:
• {module_name} module version is outdated
• Query keyword is incorrect
• The component may not exist

💡 Suggested actions:
"""

        # Add available items list (if any)
        if available_items:
            items_preview = available_items[:10]
            message += f"""
📋 Available items (first 10):
{chr(10).join(f'  • {item}' for item in items_preview)}
"""
            if len(available_items) > 10:
                message += f"\n...{len(available_items)} items in total\n"

        message += """
🔧 Advanced actions:
• Update the module via Glyphs Plugin Manager
• Restart Glyphs.app
• Check spelling (case-sensitive)
"""

        return message

    @classmethod
    def get_repositories_not_found_message(cls) -> str:
        """Get message when Repositories folder is not found

        Returns:
            Formatted explanation message
        """
        return r"""
❌ Glyphs Repositories folder not found

Repositories is where Glyphs stores plugins and modules.

🔍 Common locations:
  • Glyphs 3: ~/Library/Application Support/Glyphs 3/Repositories
  • Glyphs 2: ~/Library/Application Support/Glyphs/Repositories

💡 Solutions:

1️⃣  Verify Glyphs is installed
   • Open Glyphs.app to confirm it works properly

2️⃣  Check if the path is correct
   • Run in Terminal:
     ls -la ~/Library/Application\ Support/Glyphs\ 3/Repositories

3️⃣  Set custom path (if using non-standard location)
   • Create a .env file
   • Set environment variable:
     GLYPHS_REPOSITORIES_PATH="/your/custom/path"

4️⃣  Reinstall plugins
   • Open Glyphs Plugin Manager
   • Install required plugins and modules

📞 Still having issues?
   • Verify Glyphs version (Glyphs 3 recommended)
   • Check folder permissions
   • Try reinstalling Glyphs.app
"""

    @classmethod
    def get_update_suggestion_message(cls, module_name: str) -> str:
        """Get module update suggestion message

        Args:
            module_name: Module name

        Returns:
            Update suggestion message
        """
        return f"""
⚡ Recommended to update {module_name} module

The current {module_name} may not be the latest version.

🔄 Update methods:

1️⃣  Via Glyphs Plugin Manager
   • Window > Plugin Manager
   • Find {module_name}
   • Click the Update button

2️⃣  Update via Terminal
   pip3 install --upgrade {module_name}

💡 Restart Glyphs.app after updating to apply changes
"""

    @classmethod
    def get_glyphs_app_not_found_message(cls, headers_path: str | None = None) -> str:
        """Get message when Glyphs 3.app is not found

        Args:
            headers_path: Attempted Headers path (optional)

        Returns:
            Formatted explanation message
        """
        message = """
❌ Glyphs 3.app not found

Objective-C Headers need to be read directly from Glyphs 3.app.

🔍 Default path:
  /Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers

💡 Solutions:

1️⃣  Verify Glyphs 3 is properly installed
   • Confirm Glyphs 3.app is in the /Applications/ folder
   • Open Glyphs 3.app to confirm it works properly

2️⃣  Check installation location
   • Run in Terminal to confirm:
     ls -la "/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers"

3️⃣  Set custom path (if installed in non-standard location)
   • Create or edit .env file
   • Set environment variable:
     GLYPHS_APP_HEADERS_PATH="/your/custom/path/to/Headers"

📦 Download Glyphs 3:
   https://glyphsapp.com/

📞 Still having issues?
   • Verify Glyphs version (Glyphs 3 required)
   • Check application permissions
   • Reinstall Glyphs 3.app
"""

        if headers_path:
            message += f"""
🔎 Attempted path:
   {headers_path}
"""

        return message
