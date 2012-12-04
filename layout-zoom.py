import sublime
import sublime_plugin

class LayoutZoomCommand(sublime_plugin.TextCommand):

    def run(self, edit, op='get'):
        window = self.view.window()
        settings = sublime.load_settings('LayoutZoomStore')

        if op == 'get':
            layout = window.get_layout()

            groups = []
            for group_index in range(0, len(layout['cells'])):
                views = window.views_in_group(group_index)
                groups.append(len(views))

            # Set single layout, the "zoom" effect.
            window.set_layout({"cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]]})

            # Save state on disk
            settings.set('groups', groups)
            settings.set('layout', layout)
            sublime.save_settings('LayoutZoomStore')

        elif op == 'restore':
            layout = settings.get('layout')
            groups = settings.get('groups')

            # Restore layout
            window.set_layout(layout)

            views = window.views()

            # Restore views in layout
            view_it = 0
            for group_index in range(0, len(groups)):
                group = groups[group_index]
                for view_index in range(0, group):
                    view = views[view_it]
                    window.set_view_index(view, group_index, view_index)
                    view_it += 1