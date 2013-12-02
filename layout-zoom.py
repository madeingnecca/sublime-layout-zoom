import sublime
import sublime_plugin
import json
import os

STORAGE = sublime.packages_path() + '/User/LayoutZoomStorage.json'

class BaseLayoutCommand(sublime_plugin.WindowCommand):
    def defaultData(self):
        return {
            "windows": {}
        }

    def storageRead(self):
        data = {}

        if os.path.exists(STORAGE):
            with open(STORAGE) as f:
                data = json.loads(f.read() or '{}')

        # Merge defaultData and data.
        return dict(self.defaultData(), **data)

    def storageWrite(self,data):
        content = json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '))
        with open(STORAGE, 'w') as f:
            f.write(content)

class LayoutZoomCommand(BaseLayoutCommand):

    def zoom(self, window):
        # Set single layout, the "zoom" effect.
        window.set_layout({
            'cols': [0.0, 1.0],
            'rows': [0.0, 1.0],
            'cells': [[0, 0, 1, 1]]})

    def run(self):
        window = self.window
        wid = str(window.id())

        data = self.storageRead()

        layout = window.get_layout()

        # Remember the count of views per each group.
        groups = []
        for group_index in range(0, len(layout['cells'])):
            views = window.views_in_group(group_index)
            group = {}
            group['count'] = len(views)
            active_view = window.active_view_in_group(group_index)
            active_view_index = window.get_view_index(active_view)
            group['active_view'] = active_view_index[1]
            groups.append(group)

        active_group = window.active_group()

        self.zoom(window)

        data['windows'][wid] = {}
        data['windows'][wid]['layout'] = layout
        data['windows'][wid]['groups'] = groups
        data['windows'][wid]['active_group'] = active_group

        self.storageWrite(data)


class LayoutZoomRestoreCommand(BaseLayoutCommand):
    def run(self):
        window = self.window
        wid = str(window.id())

        data = self.storageRead()

        if not wid in data['windows']:
            return

        layout = data['windows'][wid]['layout']
        groups = data['windows'][wid]['groups']
        active_group = data['windows'][wid]['active_group']

        views = window.views()

        # Restore layout
        window.set_layout(layout)

        # Restore views in layout
        view_index = 0
        for group_index in range(len(groups)):
            group = groups[group_index]
            group_active_view = None
            for view_in_group in range(group['count']):
                view = views[view_index]
                window.set_view_index(view, group_index, view_in_group)
                view_index += 1
                if view_in_group == group['active_view']:
                    group_active_view = view
            # Give focus to group's active group.
            window.focus_view(group_active_view)
        # Give focus to the active group.
        window.focus_group(active_group)


class LayoutZoomCleanCommand(BaseLayoutCommand):
    def run(self):
        ids = [str(w.id()) for w in sublime.windows()]
        data = self.storageRead()
        wins = data['windows'].keys()

        # Window ids referencing to non-existing windows.
        diff = list(set(wins) - set(ids))

        # Remove old ids from the storage
        for winid in diff:
            data['windows'].pop(winid, None)

        # Save the storage.
        self.storageWrite(data)
