import plotly.graph_objects as go

from ..utils import validate


class CustomChart:  # noqa: H601
    """Base Class for Custom Charts."""

    annotations = []
    """Store annotations. Default is an empty list.

    See documentation: https://plot.ly/python/reference/#layout-annotations

    """

    _axis_range = {}
    _axis_range_schema = {
        'x': {
            'items': [{'type': ['integer', 'float', 'string']}, {'type': ['integer', 'float', 'string']}],
            'required': False,
            'type': 'list',
        },
        'y': {
            'items': [{'type': ['integer', 'float']}, {'type': ['integer', 'float']}],
            'required': False,
            'type': 'list',
        },
    }

    @property
    def axis_range(self):
        """Specify x/y axis range or leave as empty dictionary for autorange.

        Returns:
            dict: dictionary potentially with keys `(x, y)`

        """
        return self._axis_range

    @axis_range.setter
    def axis_range(self, axis_range):
        errors = validate(axis_range, self._axis_range_schema)
        if errors:
            raise RuntimeError(f'Validation of self.axis_range failed: {errors}')
        # Assign new axis_range
        self._axis_range = axis_range

    def __init__(self, *, title, xlabel, ylabel, layout_overrides=()):
        """Initialize Custom Dash Chart and store parameters as data members.

        Args:
            title: String title for chart (can be an empty string for blank)
            xlabel: XAxis string label (can be an empty string for blank)
            ylabel: YAxis string label (can be an empty string for blank)
            layout_overrides: Custom parameters in format [ParentKey, SubKey, Value] to customize 'go.layout'

        """
        self.title = title
        self.labels = {'x': xlabel, 'y': ylabel}
        self.layout_overrides = layout_overrides
        self.initialize_mutables()

    def initialize_mutables(self):
        """Initialize the mutable data members to prevent modifying one attribute and impacting all instances."""
        pass

    def create_figure(self, df_raw, **kwargs_data):
        """Create the figure dictionary.

        Args:
            df_raw: data to pass to formatter method
            kwargs_data: keyword arguments to pass to the data formatter method

        Returns:
            dict: keys `data` and `layout` for Dash

        """
        return {
            'data': self.create_traces(df_raw, **kwargs_data),
            'layout': go.Layout(self.apply_custom_layout(self.create_layout())),
        }

    def create_traces(self, df_raw, **kwargs_data):
        """Return traces for plotly chart.

        Should return, list: trace data points. List may be empty

        Args:
            df_raw: data to pass to formatter method
            kwargs_data: keyword arguments to pass to the data formatter method

        Raises:
            NotImplementedError: Must be overridden by child class

        """
        raise NotImplementedError('create_traces must be implemented by child class')  # pragma: no cover

    def create_layout(self):
        """Return the standard layout. Can be overridden and modified when inherited.

        Returns:
            dict: layout for Dash figure

        """
        layout = {
            'annotations': self.annotations,
            'title': go.layout.Title(text=self.title),
            'xaxis': {
                'automargin': True,
                'title': self.labels['x'],
            },
            'yaxis': {
                'automargin': True,
                'title': self.labels['y'],
                'zeroline': True,
            },
            'legend': {'orientation': 'h', 'y': -0.25},  # below XAxis label
            'hovermode': 'closest',
        }

        # Optionally apply the specified range
        for axis in ['x', 'y']:
            axis_name = f'{axis}axis'
            if axis in self.axis_range:
                layout[axis_name]['range'] = self.axis_range[axis]
            else:
                layout[axis_name]['autorange'] = True

        return layout

    def apply_custom_layout(self, layout):
        """Extend and/or override layout with custom settings.

        Args:
            layout: base layout dictionary. Typically from self.create_layout()

        Returns:
            dict: layout for Dash figure

        """
        for parent_key, sub_key, value in self.layout_overrides:
            if sub_key is not None:
                layout[parent_key][sub_key] = value
            else:
                layout[parent_key] = value

        return layout
