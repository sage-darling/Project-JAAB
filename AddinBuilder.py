'''
Project JAAB: Just Another Addin Builder

Author(s): 
Sage Darling, Nathan Clark
IDEXX Laboratories, Inc.
Westbrook, ME 04092

Utilizes a linux Github runner to build a JMP Addin with functionality to include files from other repositories.
'''

############################
#      IMPORT MODULES      #
############################

import os
import requests
import shutil
from datetime import datetime, timezone
import zipfile
import configparser

############################
#    SUPPORT FUNCTIONS     #
############################

def json_out(url, token):
    '''
    Gathers the json output based on an input url from github API.

    Args:
        url (string): A URL (weblink) that comes from the Github API in order to gather the release content information.
        token (string): Required for a private repo. This is the Github Token for authentication to access the release content.

    Returns:
        daters (list): A list of releases and the contents related to each release.

    Raises:
        Exception: Access is denied to the API and thus the data is not accessible for downstream usage.

    Example Usage:
        >>> json_out(f'https://api.github.com/repos/{owner}/{repo}/releases, f'{token}')
        [
            {
                "url": "https://api.github.com/repos/octocat/Hello-World/releases/1",
                "html_url": "https://github.com/octocat/Hello-World/releases/v1.0.0",
                "assets_url": "https://api.github.com/repos/octocat/Hello-World/releases/1/assets",
                "upload_url": "https://uploads.github.com/repos/octocat/Hello-World/releases/1/assets{?name,label}",
                "tarball_url": "https://api.github.com/repos/octocat/Hello-World/tarball/v1.0.0",
                "zipball_url": "https://api.github.com/repos/octocat/Hello-World/zipball/v1.0.0",
                "id": 1,
                "node_id": "MDc6UmVsZWFzZTE=",
                "tag_name": "v1.0.0",
                "target_commitish": "master",
                "name": "v1.0.0",
                "body": "Description of the release",
                "draft": false,
                "prerelease": false,
                "created_at": "2013-02-27T19:35:32Z",
                "published_at": "2013-02-27T19:35:32Z",
                "author": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": false
                },
                "assets": [
                {
                    "url": "https://api.github.com/repos/octocat/Hello-World/releases/assets/1",
                    "browser_download_url": "https://github.com/octocat/Hello-World/releases/download/v1.0.0/example.zip",
                    "id": 1,
                    "node_id": "MDEyOlJlbGVhc2VBc3NldDE=",
                    "name": "example.zip",
                    "label": "short description",
                    "state": "uploaded",
                    "content_type": "application/zip",
                    "size": 1024,
                    "download_count": 42,
                    "created_at": "2013-02-27T19:35:32Z",
                    "updated_at": "2013-02-27T19:35:32Z",
                    "uploader": {
                    "login": "octocat",
                    "id": 1,
                    "node_id": "MDQ6VXNlcjE=",
                    "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/octocat",
                    "html_url": "https://github.com/octocat",
                    "followers_url": "https://api.github.com/users/octocat/followers",
                    "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                    "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                    "organizations_url": "https://api.github.com/users/octocat/orgs",
                    "repos_url": "https://api.github.com/users/octocat/repos",
                    "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/octocat/received_events",
                    "type": "User",
                    "site_admin": false
                    }
                }
                ]
            }
        ]
    '''
    params = {"state":"open"}
    headers = {'Authorization':f'token {token}'}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"The data was not retrieved with status code {r.status_code}. Verify your token and try again.")
    daters = r.json()
    return(daters)

def stateDetermination(tagname):
    '''
    Takes in the tag name from the github data and looks for whether the version tag has RC, Beta or Alpha. If it does, it is test. 
    If it does not, it is production.

    Args:
        tagname (string): A string that is the version nomenclature for the release.

    Returns:
        "TEST" or "PROD" (string): the type of version which is being deployed.

    Example Usage:
        >>> stateDetermination("v1.0.5-Beta1")
        "TEST"
    '''
    # commented out release_data['prerelease'] because it's possible people might not select this check mark and it may create a prod release of a tool when it's a test release.
    #if release_data['prerelease'] == False:
    release_list = tagname.split("-")
    # if tag name doesn't have a "-", the length of the list will only be 1 long and a 2nd slot won't exist.
    if len(release_list) == 2:
        print('Release is a RC, Beta or Alpha release and will be deployed in testing.')
        return "TEST"
    else:
        print('Release is a production release and will be deployed in production.')
        return "PROD"

def verCharToNum(textVersion):
    '''
    Takes in the textVersion of the version tag from the Github Release information and converts it to a numerical version.

    Args:
        textVersion (string): A string that is the version information from the github release.

    Returns:
        numberVersion (integer): A integer that equates to the text version.

    Example Usage:
        >>> verCharToNum("V1.0.9")
        10009001
    '''
    txtVer = textVersion.replace('V','')
    #print(textVersion, txtVer)

    parts = txtVer.split('.')
    parts.reverse()
    #print(parts)

    newList = []
    for index, value in enumerate(parts):
        # print(index, value)
        if index == 0:
            base = 100000
            firstNum = int(value.split('-')[0]) * 1000
            # print('first num = ' + str(firstNum))
            try:
                preTemp = value.split('-')[1].upper()
            except:
                preTemp = value.split('-')[0].upper()
            # print(preTemp)
            preVerBase = 10
            if 'ALPHA' in preTemp:
                # print("in alpha")
                verTemp = preTemp.replace('ALPHA','')
                # print(verTemp)
                preVer = int(verTemp) * preVerBase + 2
                # print(preVer)
            elif 'BETA' in preTemp:
                #print("in beta")
                verTemp = preTemp.replace('BETA','')
                #print(verTemp)
                preVer = int(verTemp) * preVerBase + 3
                #print(preVer)
            elif 'RC' in preTemp:
                # print("in rc")
                verTemp = preTemp.replace('RC','')
                # print(verTemp)
                preVer = int(verTemp) * preVerBase + 4
                # print(preVer)
            else:
                preVer = 1
                # print(preVer)
            number = firstNum + preVer
            # print('first number is ' + str(number))
        else:
            base = 100
            # print(value,index)
            number = int(value) * (base ** (index)) * 1000
            # print(number)
        newList.append(number)
        # print(newList)
    if sum(newList) == 0:
        numberVersion = "fail"
    else:
        numberVersion = sum(newList)
    
    return(numberVersion)

def buildDate(date):
    '''
    Takes in the release date information from the Github Release information and converts it to a JMP numerical version.

    Args:
        textVersion (string): A string that is the date from the github release.

    Returns:
        numberVersion (integer): A integer that equates to the text date version in JMP format.

    Example Usage:
        >>> buildDate("2023-03-24T21:06:48Z")
        3762551208
    '''
    jmp_date = datetime(1904, 1, 1, 0, 0, 0)
    date_format_input = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

    #timezone offset - do we need this to be in EST? it will be slightly off in JMP.
    # offset = (datetime.now() - datetime.utcnow()).total_seconds()

    #seconds conversion to get to JMP seconds with the offset for the timezone.
    total_time_seconds = (date_format_input - jmp_date).total_seconds()
    total_time = int(total_time_seconds)
    return total_time

def needed_variables(json_data):
    '''
    Takes in the Github Release information and parses out necessary variables for downstream usage.

    Args:
        json_data (list): A list of information from the Github Release related to the Release being packaged.

    Returns:
        ver_num (integer): A integer that equates to the text version number from the release.
        jmp_date (integer): A integer that equates to the text date version in JMP format.
        deployment_state (string): Test or Prod deployment type.

    Example Usage:
        >>> needed_varables({release_data})
        (10009001, 3762536808, "PROD")
    '''
    ver_num = verCharToNum(json_data["tag_name"].upper())
    jmp_date = buildDate(json_data["published_at"])
    deployment_state = stateDetermination(json_data["tag_name"])
    return(ver_num, jmp_date, deployment_state)

############################
#  ADDIN BUILDER FUNCTIONS #
############################

def release_data(owner_repo, token, runid):
    '''
    Gets the release data from the Github API related to the release that triggered the action. 
    If no event triggered the action (i.e. the action was manually triggered), it defaults to the latest (which is the [0] slice).

    Args:
        owner_repo (string): the owner and repo to query for the Github Release information.
        token (string): Github authentication token produced and recognized by github for authentication to a private repo.
        runid (string): a unique code related to the release to make sure the "latest" is the one that triggered the action. 
            This is empty when the action is manually triggered and thus defaults to the latest in the list at slice 0.

    Returns:
        release(list): The specific list information to the release targetted for packaging.

    Example Usage:
        >>> release_data("octocat/Hello-World", {token}, 1)
        [
            {
                "url": "https://api.github.com/repos/octocat/Hello-World/releases/1",
                "html_url": "https://github.com/octocat/Hello-World/releases/v1.0.0",
                "assets_url": "https://api.github.com/repos/octocat/Hello-World/releases/1/assets",
                "upload_url": "https://uploads.github.com/repos/octocat/Hello-World/releases/1/assets{?name,label}",
                "tarball_url": "https://api.github.com/repos/octocat/Hello-World/tarball/v1.0.0",
                "zipball_url": "https://api.github.com/repos/octocat/Hello-World/zipball/v1.0.0",
                "id": 1,
                "node_id": "MDc6UmVsZWFzZTE=",
                "tag_name": "v1.0.0",
                "target_commitish": "master",
                "name": "v1.0.0",
                "body": "Description of the release",
                "draft": false,
                "prerelease": false,
                "created_at": "2013-02-27T19:35:32Z",
                "published_at": "2013-02-27T19:35:32Z",
                "author": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": false
                },
                "assets": [
                {
                    "url": "https://api.github.com/repos/octocat/Hello-World/releases/assets/1",
                    "browser_download_url": "https://github.com/octocat/Hello-World/releases/download/v1.0.0/example.zip",
                    "id": 1,
                    "node_id": "MDEyOlJlbGVhc2VBc3NldDE=",
                    "name": "example.zip",
                    "label": "short description",
                    "state": "uploaded",
                    "content_type": "application/zip",
                    "size": 1024,
                    "download_count": 42,
                    "created_at": "2013-02-27T19:35:32Z",
                    "updated_at": "2013-02-27T19:35:32Z",
                    "uploader": {
                    "login": "octocat",
                    "id": 1,
                    "node_id": "MDQ6VXNlcjE=",
                    "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/octocat",
                    "html_url": "https://github.com/octocat",
                    "followers_url": "https://api.github.com/users/octocat/followers",
                    "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                    "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                    "organizations_url": "https://api.github.com/users/octocat/orgs",
                    "repos_url": "https://api.github.com/users/octocat/repos",
                    "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/octocat/received_events",
                    "type": "User",
                    "site_admin": false
                    }
                }
                ]
            }
        ]
    '''
    query_url = f"https://api.github.com/repos/{owner_repo}/releases"

    release = json_out(query_url, token)

    index = 0
    slice = 0
    if runid:
        for key in release:
            #print(key)
            for keys in key:
                print(keys)
                print(key[keys])
                if key[keys] == int(runid):
                    slice = index
                    return release[slice]
            index += 1
    else:
        return release[0]

def write_release_output(data_from_release, token, save_location):
    '''
    gathers the zipball_url from the Github release output and saves it to a location for addin packaging.
    
    Args:
        data_from_release (list): The specific list information to the release targetted for packaging.
        token (string): Github authentication token produced and recognized by github for authentication to a private repo.
        save_location (string): the location where the files are being saved for packaging.

    Returns:
        os.path.join(save_location, tool_name) (string): the location created specifically for the tool where things will be packaged.
    '''
    zip_url = data_from_release['zipball_url']
    headers = {'Authorization': f'token {token}'}

    # eventually passed in through REPO name env variable so this won't matter.
    zip_url_split = zip_url.split('/')
    tool_name = zip_url_split[5]

    # change directory to save location
    os.chdir(save_location)
    zip_data = requests.get(zip_url, headers=headers)
    # open the zip name and write the contents to the folder. This is the main directory when this script is executed. Not sure how this will play out for an action.
    with open(tool_name+"_temp", "wb") as folder:
        folder.write(zip_data.content)
        folder.close()
    # extracts the zip contents and writes the contents to a directory of your choosing. 
    with zipfile.ZipFile(tool_name+"_temp", 'r') as zipped:
        zipped.extractall()
        files = zipped.namelist()
    zip_name = files[0].strip("/")
    os.rename(zip_name, tool_name)
    #print(files)
    # deletes the original zip file.
    os.remove(tool_name+"_temp")
    return os.path.join(save_location, tool_name)

def config_parse(temp_location, config_name):
    '''
    takes in the temp location where the .ini file is being stored and creates a dictionary
    
    Args:
        temp_location (string): the location where the .ini is stored. This is pulled in from the github release in the .zip file.
        config_name (string): the name that is passed in from the github action for the files list as a .ini.

    Returns:
        files_dict (dictionary): a dictionary of the needed files from the .ini file.

    Example Usage:
        Example Usage:
        >>> libs_info = config_parse(r"C://Desktop//", r"config.ini")
    '''
    source = os.path.abspath(temp_location)
    location = os.path.join(source, ".github", "workflows", config_name)

    #initialize the config parser and reading.
    config = configparser.ConfigParser()
    config.read(location)
    config.sections()
    
    #loading the variables into a dictionary to return for each variable location.
    #starting with the files needed for the libraries.
    files_dict = {}
    for keys in config['external_files']:
        new_line = config['external_files'][keys].replace("(","").replace(")","").split(",")
        key, values = keys, [s.replace(" ", "", 1) for s in new_line[0:]]
        files_dict[key] = values

    return(files_dict)

def CustomMeta(savePath, jmpBuildDate, addinState, ver_num, author, addinid, addinname, prodpath, pubpath):
    '''
    builds the custom meta data file for the addin.
    
    Args:
        savePath (string): The location in which to save the CustomMeta data file. This is the location where the addin is being packaged.
        jmpBuildDate (integer): the build date number in JMP date format.
        addinState (string): Whether this addin is "PROD" or "TEST".
        ver_num (integer): the version number of the addin.
        author (string): the author of the addin passed in as an input from the Github action.
        addinid (string): the addin id. Passed in by the github action as an input.
        addinname (string): the addin name. Passed in by the github action as an input.
        prodpath (string): the final production path where the addin will live when deployed.
        pubpath (string): the pathway where the publishedaddin.jsl lives.

    Returns:
        N/A
    '''

    customMetaDataText = '/* DO NOT EDIT THIS FILE YOURSELF AS IT IS CHANGED BY ADD-IN MANAGER */\n\nAssociative Array(\n	List(\n		List( \"addinVersion\",' + str(ver_num) + '),\n		List( \"author\",' + author + '),\n		List( \"buildDate\",' + str(jmpBuildDate) + '),\n		List( \"deployedAddinsFilename\",\"' + pubpath + '\"),\n		List( \"deployedAddinsLoc\", \"' + prodpath + '\"),\n		List( \"id\",\"' + addinid + '\"),\n		List( \"name\",\"' + addinname + '\"),\n		List( \"state\",\"' + addinState + '\")\n	)\n)'

    os.chdir(savePath)

    with open("customMetaData.jsl", "w") as file:
            file.write(customMetaDataText)
            file.close()

    print("Custom Meta Data has been written to the location.")

def AddinDef(savePath, version_num, addinid, addinname):
    '''
    builds the addin.def for the addin.
    
    Args:
        savePath (string): The location in which to save the CustomMeta data file. This is the location where the addin is being packaged.
        ver_num (integer): the version number of the addin.
        addinid (string): the addin id. Passed in by the github action as an input.
        addinname (string): the addin name. Passed in by the github action as an input.

    Returns:
        N/A
    '''
    addin_def_text = 'id=' + addinid + '\n' + 'name=' + addinname + '\n' + "addinVersion=" + str(version_num)
    
    os.chdir(savePath)

    with open("addin.def", "w") as file:
            file.write(addin_def_text)
            file.close()

def JMPCust(savePath, tag_version, addinID, jmpcustfilename):
    '''
    builds the addin.jmpcust for the addin.
    
    Args:
        savePath (string): The location in which to save the JMPCust data file. This is the location where the addin is being packaged.
        tag_version (string): The string version of the tag version of the JMP Addin.
        addinID (string): The string input for the addin ID that will be used for the path. 
        jmpcustfilename (string): The filename that links to the JMP cust file to build the menu for the addin.

    Returns:
        N/A
    '''
    source = os.path.abspath(savePath)
    location = os.path.join(source, ".github", "workflows")
    # variables for the text to search for and the one to replace.

    os.chdir(location)

    search_text_tooltag  = "TOOLTAG"
    search_text_addin = "AdDinIDDoNotTouCHY"
    replace_text_tooltag  = tag_version
    replace_text_addin = addinID

    with open(jmpcustfilename, 'r') as file:
            data = file.read()
            data_new = data.replace(search_text_tooltag, replace_text_tooltag)
            data_round_2 = data_new.replace(search_text_addin, replace_text_addin)
            file.close()

    os.chdir(savePath)

    with open('addin.jmpcust', 'w') as new_file:
        new_file.write(data_round_2)
        new_file.close()

def uploadAsset(addinFinalName, releaseDictionary, addinLocation, token):
    '''
    uploads the completed JMP addin to the github release as an asset.
    
    Args:
        addinFinalName (string): The name that the addin will be called as a filename.
        releaseDictionary (list): The list of the release information for the URL of where to upload assets.
        addinLocation (string): the location where the addin package is location.
        token (string): Github authentication token produced and recognized by github for authentication to a private repo.

    Returns:
        N/A
    '''
    os.chdir(addinLocation)
    uploadLink = releaseDictionary['upload_url'].split(u"{")[0] + "?name=" + addinFinalName
    print(uploadLink)
    headers = {
        'Content-Type': 'zip',
        'Authorization': f'token {token}'
        }
    response = requests.post(uploadLink, headers=headers, data=open(addinFinalName, 'rb'))

def pack_up_externals(externalsDict, runnerlocation, token):
    '''
    takes in a dictionary of external files with relevant information needed and pulls the files to compile.

    Args:
        externalDict (dictionary): a dictionary of external files produced from config_parser.
        runnerlocation (string): The file folder location where the final addin is being packaged.
        token(string): Github authentication token produced and recognized by github for authentication to a private repo.

    Returns:
        NA

    Example Usage:
        >>> pack_up_externals(external_files, Token)
    '''
    for numbah, maps in externalsDict.items():
        if len(maps) != 6:
            raise ValueError('One of the external files input into the .ini file in the repository is short an input. Please correct and try again.')
        repo_owner = maps[0]
        repo_name = maps[1]
        needed_file = maps[2]
        name_it_this = maps[3]
        folder_name = maps[4]
        version_we_want = maps[5]
        files_from_repo = externals_data(repo_owner + r'/' + repo_name, token, version_we_want)
        write_external(files_from_repo, needed_file, name_it_this, folder_name, runnerlocation, token)
               
def externals_data(owner_repo, token, version="latest"):
    '''
    gathers the data in a dictionary related to the files needed to be packaged in the final Addin from another owner and repo.
    
    Args:
        owner_repo (string): the owner and repo to query for the Github Release information.
        token (string): Github authentication token produced and recognized by github for authentication to a private repo.
        version (string): defaults to latest. Can be overruled to be whatever version of the file is needed.

    Returns:
        a dictionary with the filename, download URL, and filetype for the library files.

    Example Usage:
        >>> libs_info = libs_data("octocat/libraries", TOKEN, main_vars['lib_tag'])
    '''
    # start with a blank dictionary
    repo_dict = {}

    # gets the latest libraries or gets the libraries based on version tag if applicable.
    if version.lower() == "latest":
        query_url = f"https://api.github.com/repos/{owner_repo}/contents/"
    else:
        query_url = f"https://api.github.com/repos/{owner_repo}/contents?ref={version}"
    libs_head = json_out(query_url, token)

    #print(libs_head)
    # add the files into the dictionary for searching later.
    for file in libs_head:
        filename = str(file["name"])
        download_url = str(file["download_url"])
        file_type = str(file["type"])
        if(file_type == "dir" ):
            query_url_folder = f"https://api.github.com/repos/{owner_repo}/contents/{filename}/"
            libs_folder = json_out(query_url_folder, token)
            # add the files into the dictionary for the folder if contents are necessary
            for folders in libs_folder:
                filename = str(folders["name"])
                download_url = str(folders["download_url"])
                file_type = str(folders["type"])
                repo_dict[filename] = [file_type, download_url]
        #add new value/keys to the dictionary, [0] slice is always filetype and [1] is download_url
        repo_dict[filename] = [file_type, download_url]

    # add folder info to the dictionary below if it is necessary.
    # pprint(repo_dict)
    return(repo_dict)

def write_external(filename_dict, needed_file_from_repo, final_name_of_file, folder_to_place, starting_dest_folder, token):
    '''
    writes the necessary libraries or utilities in the necessary location inside the folder for addin.
    
    Args:
        filename_dict (dictionary): the dictionary created from externals_data that contains the files from the repo to download.
        needed_file_from_repo (string): the name of the file needed from the repository.
        final_name_of_file (string): the name to name the file in the addin.
        folder_to_place (string): the folder to place the file in the addin.
        starting_dest_folder (string): the place where the addin is being built.
        token (string): Github authentication token produced and recognized by github for authentication to a private repo.

    Returns:
        N/A
    '''
    os.chdir(starting_dest_folder)
    dictionary_url_num = 1

    target_location = filename_dict[needed_file_from_repo][dictionary_url_num]
    file = requests.get(str(target_location), token)
    if folder_to_place.lower() == "main":
        complete_file_folder = starting_dest_folder
    else: 
        complete_file_folder = os.path.join(starting_dest_folder, folder_to_place)
    #create new folder if it does not exist
    if os.path.exists(complete_file_folder) == False:
        os.makedirs(complete_file_folder)
    complete_file = os.path.join(complete_file_folder, final_name_of_file)
    with open(complete_file, "wb") as files:
        files.write(file.content)
        files.close()

############################
#           MAIN           #
############################

def main():

    ############################
    #  ENVIRONMENT VARIABLES   #
    ############################
    # passed in environmental variables from git.
    TOKEN = os.environ['Token']
    OWNER_REPO = os.environ['OwnerRepo']
    RUN_ID = os.environ['RunID']
    MAKE_META_FILE = os.environ['MakeMetaFile']
    PROD_PATH = os.environ['ProdPath']
    PUB_PATH = os.environ['PubPath']
    ADDIN_ID = os.environ['AddinID']
    ADDIN_NAME = os.environ['AddinName']
    AUTHOR = os.environ['Author']
    EXTERNAL_FILES = os.environ['ExternalFiles']
    TAG_SUFFIX = os.environ['TagSuffix']
    JMP_CUST_FILE = os.environ['JmpCust']

    ############################
    #        Full Flow         #
    ############################
    save_location = os.getcwd()
    data = release_data(OWNER_REPO, TOKEN, RUN_ID)
    ver_num, jmp_date, deployment_stage = needed_variables(data)
    zip_location = write_release_output(data, TOKEN, save_location)

    # write the Custom Meta Data (if applicable), Addin.def and JMP.cust files to the addin location.
    if MAKE_META_FILE != "0":
        CustomMeta(zip_location, jmp_date, deployment_stage, ver_num, AUTHOR, ADDIN_ID, ADDIN_NAME, PROD_PATH, PUB_PATH)
    
    AddinDef(zip_location, ver_num, ADDIN_ID, ADDIN_NAME)
    JMPCust(zip_location, data["tag_name"], ADDIN_ID, JMP_CUST_FILE)

    if EXTERNAL_FILES != "":
        print("a .ini file is referenced for include files")
        external_files_dict = config_parse(zip_location, EXTERNAL_FILES)
    else:
        external_files_dict = {}
    
    # delete the .github files as they are no longer needed for the build.
    shutil.rmtree('.github')

    # write the library files
    if len(external_files_dict) != 0:
        print("Library files are detected in the config.ini and will be included")
        pack_up_externals(external_files_dict, zip_location, TOKEN)

    # zip up the addin files to create the addin
    if int(TAG_SUFFIX) == 1:
        addin_final = ADDIN_NAME + "_" + data["tag_name"]
    elif int(TAG_SUFFIX) == 0 and deployment_stage == "TEST":
        addin_final = ADDIN_NAME + "_" + data["tag_name"]
    else:
        addin_final = ADDIN_NAME

    os.chdir(save_location)
    shutil.make_archive(addin_final, 'zip', OWNER_REPO.split("/")[1])
    os.rename(addin_final + '.zip', addin_final + '.jmpaddin')
    addinFinalName = addin_final + '.jmpaddin'

    print(f"addin build is complete for {addinFinalName}")

    # upload the final addin to Github.
    uploadAsset(addinFinalName, data, save_location, TOKEN)

    print(f"{addinFinalName} is uploaded to Git.")

if __name__ == "__main__":
    main()