from mule.task import ITask
import pystache
from pkg_resources import resource_filename
from mule.util import git_util
import textwrap
from mule.util import file_util
from mule.util import github_util

class GenerateReleaseNotes(ITask):

    required_fields = [
        'releaseVersion',
        'githubPatToken',
        'githubRepoFullName'
    ]
    assetFolderPath = 'assets'

    def __init__(self, args):
        super().__init__(args)
        self.releaseVersion = args['releaseVersion']
        self.githubPatToken = args['githubPatToken']
        self.githubRepoFullName = args['githubRepoFullName']

        if 'assetFolderPath' in args:
            self.assetFolderPath = args['assetFolderPath']

    def formatCommitMessages(self, commits):
        commit_messages = ""
        for commit in commits:
            message_title = commit.message.split('\n')[0]
            message_body = '\n'.join(commit.message.split('\n')[1:])
            indented_message_body = textwrap.indent(message_body, "\t")
            commit_messages += f"* [{message_title}]({commit.hexsha})\n{indented_message_body}\n"
        return commit_messages

    def execute(self, job_context):
        super().execute(job_context)
        commits = git_util.getCommitsSinceLastTag()
        changes = self.formatCommitMessages(commits)
        head_commit_hash = git_util.getHeadCommitHash()
        values = {
            'changes': changes,
            'commit_hash': head_commit_hash,
            'repo_full_name': self.githubRepoFullName
        }
        template_path = resource_filename(__name__, 'resources/notes.template.mustache')
        mustache_file = file_util.readFileAsString(template_path)
        release_notes = pystache.render(mustache_file, values)
        github_util.createGithubReleaseForCurrentRepo(self.githubPatToken, self.githubRepoFullName, head_commit_hash, self.releaseVersion, release_notes, self.assetFolderPath)
