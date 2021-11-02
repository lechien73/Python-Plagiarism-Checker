import os
from github import Github


def get_urls(repo_name):

    g = Github(os.environ.get("GITHUB_API_KEY"))
    base_url = os.environ.get("REPO_BASE")

    repo = g.get_repo(base_url + repo_name)
    contents = repo.get_contents("")
    urls = []

    ignore = ["Procfile", "bootstrap.min.js", "bootstrap.min.css",
            "materialize.min.js", "materialize.min.css", "animations.css", 
            "png", "jpg", "manage.py","custom_storages.py", "wsgi.py",
            "settings.py", "0001_initial.py", "mp4", "avi", "m4v", "mp3", 
            "stripe.js", "pdf", "xd", "wav", "jquery.min.js", "jquery-3.5.0.js",
            "jasmine.js", "jasmine-html.js", "xterm.css", "xterm.js"]

    # Build list of urls of raw source code files to be scanned
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir" and file_content.name != '.vscode':
            contents.extend(repo.get_contents(file_content.path))
        else:
            if file_content.name not in ignore:
                if file_content.name.split('.')[-1] in ['html', 'css', 'js', 'py']:
                    urls.append(file_content.download_url)
    
    return urls
