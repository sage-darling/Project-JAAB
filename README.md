# Project-JAAB = Just Another Addin Builder
This action is used to retrieve files from the github repository that is using the action in order to package them to create a JMP Addin to be used with [JMP Software](https://www.jmp.com/en_us/home.html).

## Whatcha Lookin' For?
- [Mandatory Prerequisites](#Mandatory-Prerequisites)
- [Optional Prerequisites](#optional-prerequisites)

## Mandatory Prerequisites
Before building an addin with the Project-JAAB action, the following prerequisities must be met:
**GitHub Token:**
A token is required as an input to Project-JAAB when accessing private repositories for the addin compilation. This will be passed into the action as an input under `token`. Github documentation related to managing and creating personal access tokens can be found [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#about-personal-access-tokens). The token should have read and write permissions. 
After an access token is created, it can be added to the repository utilizing the action by navigating to the repository -> Settings -> Secrets and variables -> Actions -> New repository secret

**Text File in .github/workflows of the Repository to describe the JMP Addin Menu Format**
This text file should be located in the .github/workflows and can be named any name. This name will be input in the `jmpcust_txt_file` input field and is a required input. This file allows for flexibility for how the JMP Menu looks and where the addin is added and shows to the user.

Basic File format WITHOUT edits:
`
<!-- JMP Add-In Builder created --><jm:menu_and_toolbar_customizations xmlns:jm="http://www.jmp.com/ns/menu" version="3">
<jm:insert_in_main_menu>
    <jm:insert_after>
        <jm:name></jm:name>
        <jm:menu>

            <jm:name>[Header Name]</jm:name>
                <jm:caption>[Header Name]</jm:caption>
            <jm:menu>
                <jm:name>[Menu Item Name]</jm:name>
                    <jm:caption>[Menu Item Name]</jm:caption>
                <jm:command>
                    <jm:name>[addin name everyone sees]</jm:name>
                        <jm:caption>[addin name everyone sees] TOOLTAG</jm:caption>
                        <jm:action type="path">$ADDIN_HOME(AdDinIDDoNotTouCHY)\[name of jsl file in addin].jsl</jm:action>
                        <jm:tip>[Write a caption to describe the addin]</jm:tip>
                        <jm:icon type="builtin">[Choose a symbol]</jm:icon>
                </jm:command>
            </jm:menu>
            
        </jm:menu>
    </jm:insert_after>
</jm:insert_in_main_menu>
</jm:menu_and_toolbar_customizations>
`
What does this file look like?:

How to make the necessary edits:
`[Header Name]`: edit this area of the template to say the naming you would like in the overarching menu location. This is the first section individuals will see and is the header item. In the case above, this is `Header Item`.

`[Menu Item Name]`: edit this area to be the next menu item that will be after the person selects whatever the `[Header Name]` is. In the case of above, this is `Menu Item Name`.

`[addin name everyone sees]`: edit this to be the name you want everyone to see for this addin. It doesn't need to match anything anywhere else but this is how the person will recognize this addin to use. In the case of above, this is `addin name everyone sees`. **IMPORTANT NOTE: Do not edit the TOOLTAG part of this line in the template. Only edit the [addin name everyone sees] part. TOOLTAG automatically adds the version info to the naming, should `tag_suffix` input from the action be 1**

`AdDinIDDoNotTouCHY`: This key says Do Not Touchy for a reason. Therefore, do not touchy. This value is pulled from input `addin_id` from the action. Typically it is something along the lines of `com.companyname.uniquetoolname`.

`[name of jsl file in addin]`: edit this to be the name of the .jsl you are packaging as the addin. This is the .jsl code you have written and want JMP to recognize and execute when a person clicks this button. Because of the path information above, you only need the jsl name here. Make sure to keep the `.jsl` at the end so that JMP will recognize the code to execute. If this does not match your jsl filename, the button becomes effectively useless.

`[Write a caption to describe the addin]`: edit this to say whatever you want! When a person hovers in JMP over the `[addin name everyone sees]` this caption will appear to describe what the addin does. Try to keep this as a relatively short description. 1 sentence tops. The above example shows "Write a caption to describe the addin"

`[Choose a symbol]`: Here you can get creative about what you want your symbol to look like! This is the symbol that exists next to `addin name everyone sees`. JMP has many `"builtin"` ones you can leverage by using the name that JMP recognizes. If you are unsure, an Addin exists [here](https://community.jmp.com/t5/JMP-Add-Ins/Built-In-JMP-Icons/ta-p/42251#:~:text=Description,be%20set%20as%20window%20icons.) that can help you pick what this is. Find your symbol from this addin, click it, find the Icon Name, and paste that into the `[Choose a symbol]` location.

Now your jmpcust.txt is complete! :sparkles: :sparkles:

## Optional Prerequisites
**A .ini file**


## Inputs
