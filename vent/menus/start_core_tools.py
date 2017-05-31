import npyscreen
import threading
import time

from vent.api.actions import Action
from vent.api.plugins import Plugin
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Images
from vent.helpers.meta import Tools

class StartCoreToolsForm(npyscreen.ActionForm):
    """ For picking which tools to start """
    tools_tc = {}
    triggered = 0
    logger = Logger(__name__)

    def create(self):
        self.add_handlers({"^T": self.change_forms, "^Q": self.quit})
        self.add(npyscreen.TitleText, name='Select which tools to start (only enabled, built, non-running core tools are shown):', editable=False)

    def while_waiting(self):
        """ Update with current tools that are cores """
        if not self.triggered:
            i = 4
            api_action = Action()
            inventory = api_action.inventory(choices=['repos', 'tools', 'built', 'enabled', 'running', 'core'])
            for repo in inventory['repos']:
                repo_name = repo.rsplit("/", 2)[1:]
                self.tools_tc[repo] = {}
                title_text = self.add(npyscreen.TitleText, name='Plugin: '+repo, editable=False, rely=i, relx=5)
                title_text.display()
                i += 1
                for tool in inventory['tools']:
                    r_name = tool[0].split(":")
                    if repo_name[0] == r_name[0] and repo_name[1] == r_name[1]:
                        core = False
                        running = False
                        built = False
                        enabled = False
                        for item in inventory['core']:
                            if tool[0] == item[0]:
                                core = True
                        for item in inventory['running']:
                            if tool[0] == item[0] and item[2] == 'running':
                                running = True
                        for item in inventory['built']:
                            if tool[0] == item[0] and item[2] == 'yes':
                                built = True
                        for item in inventory['enabled']:
                            if tool[0] == item[0] and item[2] == 'yes':
                                enabled = True
                        t = tool[1]
                        if t == "":
                            t = "/"
                        if core and not running and built and enabled:
                            t += ":" + ":".join(tool[0].split(":")[-2:])
                            self.tools_tc[repo][t] = self.add(npyscreen.CheckBox, name=t, value=True, relx=10)
                            self.tools_tc[repo][t].display()
                            i += 1
                i += 2
            self.triggered = 1
        return

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm("MAIN")

    def on_ok(self):
        """
        Take the tool selections and start them
        """
        def diff(first, second):
            """
            Get the elements that exist in the first list and not in the second
            """
            second = set(second)
            return [item for item in first if item not in second]

        def popup(original, orig_type, thr, title):
            """
            Start the thread and display a popup of info
            until the thread is finished
            """
            thr.start()
            info_str = ""
            while thr.is_alive():
                if orig_type == 'containers':
                    info = diff(Containers(), original)
                elif orig_type == 'images':
                    info = diff(Images(), original)
                if info:
                    info_str = ""
                for entry in info:
                    # TODO limit length of info_str to fit box
                    info_str += entry[0]+": "+entry[1]+"\n"
                npyscreen.notify_wait(info_str, title=title)
                time.sleep(1)
            return

        original_containers = Containers()

        api_action = Action()
        tool_dict = {}
        for repo in self.tools_tc:
            for tool in self.tools_tc[repo]:
                self.logger.info(tool)
                if self.tools_tc[repo][tool].value:
                    t = tool
                    if t.startswith('/:'):
                        t = " "+t[1:]
                    t = t.split(":")
                    tool_dict.update(api_action.prep_start(name=t[0], branch=t[1], version=t[2]))
        thr = threading.Thread(target=api_action.start, args=(), kwargs={'tool_dict':tool_dict})
        popup(original_containers, "containers", thr,
              'Please wait, starting containers...')
        npyscreen.notify_confirm("Done starting containers.",
                                 title='Started containers')
        self.quit()

    def on_cancel(self):
        self.quit()

    def change_forms(self, *args, **keywords):
        """ Toggles to main """
        change_to = "MAIN"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)