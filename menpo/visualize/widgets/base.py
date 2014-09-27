from .helpers import (figure_options, format_figure_options, channel_options,
                      format_channel_options, update_channel_options,
                      landmark_options, format_landmark_options,
                      update_landmark_options, info_print, format_info_print,
                      model_parameters, format_model_parameters,
                      update_model_parameters, final_result_options,
                      format_final_result_options, update_final_result_options,
                      iterations_result_options,
                      format_iterations_result_options,
                      update_iterations_result_options, animation_options,
                      format_animation_options, plot_options,
                      format_plot_options, update_plot_options)
from IPython.html.widgets import (interact, IntSliderWidget, PopupWidget,
                                  ContainerWidget, TabWidget,
                                  RadioButtonsWidget, CheckboxWidget)
from IPython.display import display, clear_output
import matplotlib.pylab as plt
from menpo.visualize.viewmatplotlib import MatplotlibSubplots
import numpy as np
from collections import OrderedDict

# This glyph import is called frequently during visualisation, so we ensure
# that we only import it once
glyph = None


def visualize_images(images, figure_size=(7, 7), popup=False, **kwargs):
    r"""
    Widget that allows browsing through a list of images.

    Parameters
    -----------
    images : `list` of :map:`Image` or subclass
        The list of images to be displayed. Note that the images can have
        different attributes between them, i.e. different landmark groups and
        labels, different number of channels etc.

    figure_size : (`int`, `int`), optional
        The initial size of the plotted figures.

    popup : `boolean`, optional
        If enabled, the widget will appear as a popup window.

    kwargs : `dict`, optional
        Passed through to the viewer.
    """
    from menpo.image import MaskedImage

    # make sure that images is a list even with one image member
    if not isinstance(images, list):
        images = [images]

    # find number of images
    n_images = len(images)

    # define plot function
    def plot_function(name, value):
        # get selected image number
        im = 0
        if n_images > 1:
            im = image_number_wid.selected_index

        # update info text widget
        update_info(images[im],
                    channel_options_wid.image_is_masked,
                    landmark_options_wid.group)

        # show image with selected options
        _plot_figure(image=images[im],
                     image_enabled=True,
                     landmarks_enabled=landmark_options_wid.landmarks_enabled,
                     image_is_masked=channel_options_wid.image_is_masked,
                     masked_enabled=channel_options_wid.masked_enabled,
                     channels=channel_options_wid.channels,
                     glyph_enabled=channel_options_wid.glyph_enabled,
                     glyph_block_size=channel_options_wid.glyph_block_size,
                     glyph_use_negative=channel_options_wid.glyph_use_negative,
                     sum_enabled=channel_options_wid.sum_enabled,
                     groups=[landmark_options_wid.group],
                     with_labels=[landmark_options_wid.with_labels],
                     groups_colours=dict(),
                     subplots_enabled=False,
                     subplots_titles=dict(),
                     image_axes_mode=True,
                     legend_enabled=landmark_options_wid.legend_enabled,
                     x_scale=figure_options_wid.x_scale,
                     y_scale=figure_options_wid.x_scale,
                     axes_visible=figure_options_wid.axes_visible,
                     figure_size=figure_size,
                     **kwargs)

    # define function that updates info text
    def update_info(image, image_is_masked, group):
        # prepare masked (or non-masked) str
        masked_str = "Image"
        if image_is_masked:
            masked_str = "Masked image"

        # prepare channels str
        ch_str = 'channels'
        if image.n_channels == 1:
            ch_str = 'channel'

        # create info str
        txt = "$\\bullet~\\texttt{" + \
              "{} of size {} with {} {}".format(masked_str, image._str_shape,
                                                image.n_channels, ch_str) + \
              ".}\\\\ \\bullet~\\texttt{" + \
              "{}".format(image.landmarks[group].lms.n_points) + \
              " landmark points.}\\\\ "
        if image_is_masked:
            txt += "\\bullet~\\texttt{" + \
                   "{} masked pixels.".format(image.n_true_pixels) + "}\\\\ "
        txt += "\\bullet~\\texttt{min=" + \
               "{0:.3f}".format(image.pixels.min()) + ", max=" + \
               "{0:.3f}".format(image.pixels.max()) + "}$"

        # update info widget text
        info_wid.children[1].value = txt

    # create options widgets
    channel_options_wid = channel_options(images[0].n_channels,
                                          isinstance(images[0], MaskedImage),
                                          plot_function,
                                          masked_default=False,
                                          toggle_show_default=True,
                                          toggle_show_visible=False)
    all_groups_keys, all_labels_keys = _extract_groups_labels(images[0])
    landmark_options_wid = landmark_options(all_groups_keys, all_labels_keys,
                                            plot_function,
                                            toggle_show_default=True,
                                            landmarks_default=True,
                                            legend_default=True,
                                            toggle_show_visible=False)
    figure_options_wid = figure_options(plot_function, scale_default=1.,
                                        show_axes_default=False,
                                        toggle_show_default=True,
                                        figure_scale_bounds=(0.1, 2),
                                        figure_scale_step=0.1,
                                        figure_scale_visible=True,
                                        toggle_show_visible=False)
    info_wid = info_print(toggle_show_default=True,
                          toggle_show_visible=False)

    # define function that updates options' widgets state
    def update_widgets(name, value):
        # get new groups and labels, update landmark options and format them
        group_keys, labels_keys = _extract_groups_labels(images[value])
        update_landmark_options(landmark_options_wid, group_keys, labels_keys,
                                plot_function)
        format_landmark_options(landmark_options_wid, container_padding='6px',
                                container_margin='6px',
                                container_border='1px solid black',
                                toggle_button_font_weight='bold',
                                border_visible=False)
        # update channel options
        update_channel_options(channel_options_wid,
                               n_channels=images[value].n_channels,
                               image_is_masked=isinstance(images[value],
                                                          MaskedImage))

    # create final widget
    if n_images > 1:
        # image selection slider
        image_number_wid = animation_options(
            index_min_val=0, index_max_val=n_images-1,
            plot_function=plot_function, update_function=update_widgets,
            index_step=1, index_default=0,
            index_description='Image Number', index_minus_description='<',
            index_plus_description='>', index_style='buttons',
            index_text_editable=True, loop_default=True, interval_default=0.3,
            toggle_show_title='Image Options', toggle_show_default=True,
            toggle_show_visible=False)

        # final widget
        cont_wid = TabWidget(children=[info_wid, channel_options_wid,
                                       landmark_options_wid,
                                       figure_options_wid])
        wid = ContainerWidget(children=[image_number_wid, cont_wid])
        button_title = 'Images Menu'
    else:
        # final widget
        wid = TabWidget(children=[info_wid, channel_options_wid,
                                  landmark_options_wid, figure_options_wid])
        button_title = 'Image Menu'
    # create popup widget if asked
    if popup:
        wid = PopupWidget(children=[wid], button_text=button_title)

    # display final widget
    display(wid)

    # set final tab titles
    tab_titles = ['Image info', 'Channels options', 'Landmarks options',
                  'Figure options']
    if popup:
        if n_images > 1:
            for (k, tl) in enumerate(tab_titles):
                wid.children[0].children[1].set_title(k, tl)
        else:
            for (k, tl) in enumerate(tab_titles):
                wid.children[0].set_title(k, tl)
    else:
        if n_images > 1:
            for (k, tl) in enumerate(tab_titles):
                wid.children[1].set_title(k, tl)
        else:
            for (k, tl) in enumerate(tab_titles):
                wid.set_title(k, tl)

    # align-start the image number widget and the rest
    if n_images > 1:
        wid.add_class('align-start')

    # format options' widgets
    if n_images > 1:
        format_animation_options(image_number_wid, index_text_width='0.5cm',
                                 container_padding='6px',
                                 container_margin='6px',
                                 container_border='1px solid black',
                                 toggle_button_font_weight='bold',
                                 border_visible=False)
    format_channel_options(channel_options_wid, container_padding='6px',
                           container_margin='6px',
                           container_border='1px solid black',
                           toggle_button_font_weight='bold',
                           border_visible=False)
    format_landmark_options(landmark_options_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=False)
    format_figure_options(figure_options_wid, container_padding='6px',
                          container_margin='6px',
                          container_border='1px solid black',
                          toggle_button_font_weight='bold',
                          border_visible=False)
    format_info_print(info_wid, font_size_in_pt='9pt', container_padding='6px',
                      container_margin='6px',
                      container_border='1px solid black',
                      toggle_button_font_weight='bold', border_visible=False)

    # update widgets' state for image number 0
    update_widgets('', 0)

    # Reset value to trigger initial visualization
    landmark_options_wid.children[1].children[1].value = False


def visualize_shape_model(shape_models, n_parameters=5,
                          parameters_bounds=(-3.0, 3.0), figure_size=(7, 7),
                          mode='multiple', popup=False, **kwargs):
    r"""
    Allows the dynamic visualization of a multilevel shape model.

    Parameters
    -----------
    shape_models : `list` of :map:`PCAModel` or subclass
        The multilevel shape model to be displayed. Note that each level can
        have different number of components.

    n_parameters : `int` or `list` of `int` or None, optional
        The number of principal components to be used for the parameters
        sliders.
        If int, then the number of sliders per level is the minimum between
        n_parameters and the number of active components per level.
        If list of int, then a number of sliders is defined per level.
        If None, all the active components per level will have a slider.

    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.

    figure_size : (`int`, `int`), optional
        The size of the plotted figures.

    mode : 'single' or 'multiple', optional
        If single, only a single slider is constructed along with a drop down
        menu.
        If multiple, a slider is constructed for each parameter.

    popup : `boolean`, optional
        If enabled, the widget will appear as a popup window.

    kwargs : `dict`, optional
        Passed through to the viewer.
    """
    # make sure that shape_models is a list even with one member
    if not isinstance(shape_models, list):
        shape_models = [shape_models]

    # find number of levels (i.e. number of shape models)
    n_levels = len(shape_models)

    # find maximum number of components per level
    max_n_params = [sp.n_active_components for sp in shape_models]

    # check given n_parameters
    # the returned n_parameters is a list of len n_levels
    n_parameters = _check_n_parameters(n_parameters, n_levels, max_n_params)

    # Define plot function
    def plot_function(name, value):
        # get params
        level = 0
        if n_levels > 1:
            level = level_wid.value
        def_mode = mode_wid.value
        axis_mode = axes_mode_wid.value
        parameters_values = model_parameters_wid.parameters_values
        x_scale = figure_options_wid.x_scale
        y_scale = figure_options_wid.y_scale
        axes_visible = figure_options_wid.axes_visible

        # compute weights
        weights = parameters_values * shape_models[level].eigenvalues[:len(parameters_values)] ** 0.5

        # clear current figure
        clear_output(wait=True)

        # invert axis if image mode is enabled
        if axis_mode == 1:
            plt.gca().invert_yaxis()

        # compute and show instance
        if def_mode == 1:
            # Deformation mode
            # compute instance
            instance = shape_models[level].instance(weights)

            # plot
            if mean_wid.value:
                shape_models[level].mean.view(image_view=axis_mode == 1,
                                              colour_array='y', **kwargs)
                plt.hold = True
            instance.view(image_view=axis_mode == 1, **kwargs)

            # instance range
            tmp_range = instance.range()
        else:
            # Vectors mode
            # compute instance
            instance_lower = shape_models[level].instance([-p for p in weights])
            instance_upper = shape_models[level].instance(weights)

            # plot
            shape_models[level].mean.view(image_view=axis_mode == 1, **kwargs)
            plt.hold = True
            for p in range(shape_models[level].mean.n_points):
                xm = shape_models[level].mean.points[p, 0]
                ym = shape_models[level].mean.points[p, 1]
                xl = instance_lower.points[p, 0]
                yl = instance_lower.points[p, 1]
                xu = instance_upper.points[p, 0]
                yu = instance_upper.points[p, 1]
                if axis_mode == 1:
                    # image mode
                    plt.plot([ym, yl], [xm, xl], 'r-', lw=2)
                    plt.plot([ym, yu], [xm, xu], 'g-', lw=2)
                else:
                    # point cloud mode
                    plt.plot([xm, xl], [ym, yl], 'r-', lw=2)
                    plt.plot([xm, xu], [ym, yu], 'g-', lw=2)

            # instance range
            tmp_range = shape_models[level].mean.range()

        plt.hold = False
        plt.gca().axis('equal')
        # set figure size
        plt.gcf().set_size_inches([x_scale, y_scale] * np.asarray(figure_size))
        # turn axis on/off
        if not axes_visible:
            plt.axis('off')
        plt.show()

        # change info_wid info
        txt = "$\\bullet~\\texttt{Level: " + "{}".format(level+1) + \
              " out of " + "{}".format(n_levels) + \
              ".}\\\\ \\bullet~\\texttt{" + \
              "{}".format(shape_models[level].n_components) + \
              " components in total.}\\\\ \\bullet~\\texttt{" + \
              "{}".format(shape_models[level].n_active_components) + \
              " active components.}\\\\ \\bullet~\\texttt{" + \
              "{0:.1f}".format(shape_models[level].variance_ratio*100) + \
              "% variance kept.}\\\\ \\bullet~\\texttt{Instance range: " + \
              "{0:.1f} x {1:.1f}".format(tmp_range[0], tmp_range[1]) + \
              ".}\\\\ \\bullet~\\texttt{" + \
              "{}".format(shape_models[level].mean.n_points) + \
              " landmark points, " + \
              "{}".format(shape_models[level].n_features) + " features.}$"
        info_wid.children[1].value = txt

    # Plot eigenvalues function
    def plot_eigenvalues(name):
        # get parameters
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # show eigenvalues plots
        _plot_eigenvalues(shape_models[level], figure_size,
                          figure_options_wid.x_scale,
                          figure_options_wid.y_scale)

    # create options widgets
    mode_dict = OrderedDict()
    mode_dict['Deformation'] = 1
    mode_dict['Vectors'] = 2
    mode_wid = RadioButtonsWidget(values=mode_dict, description='Mode:',
                                  value=1)
    mode_wid.on_trait_change(plot_function, 'value')
    mean_wid = CheckboxWidget(value=False, description='Show mean shape')
    mean_wid.on_trait_change(plot_function, 'value')

    # controls mean shape checkbox visibility
    def mean_visible(name, value):
        if value == 1:
            mean_wid.disabled = False
        else:
            mean_wid.disabled = True
            mean_wid.value = False
    mode_wid.on_trait_change(mean_visible, 'value')
    model_parameters_wid = model_parameters(n_parameters[0], plot_function,
                                            params_str='param ', mode=mode,
                                            params_bounds=parameters_bounds,
                                            toggle_show_default=True,
                                            toggle_show_visible=False,
                                            plot_eig_visible=True,
                                            plot_eig_function=plot_eigenvalues)
    figure_options_wid = figure_options(plot_function, scale_default=1.,
                                        show_axes_default=True,
                                        toggle_show_default=True,
                                        toggle_show_visible=False)
    axes_mode_wid = RadioButtonsWidget(values={'Image': 1, 'Point cloud': 2},
                                       description='Axes mode:', value=1)
    axes_mode_wid.on_trait_change(plot_function, 'value')
    ch = list(figure_options_wid.children)
    ch.insert(3, axes_mode_wid)
    figure_options_wid.children = ch
    info_wid = info_print(toggle_show_default=True, toggle_show_visible=False)

    # define function that updates options' widgets state
    def update_widgets(name, value):
        update_model_parameters(model_parameters_wid, n_parameters[value],
                                plot_function, params_str='param ')

    # create final widget
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = RadioButtonsWidget(values=radio_str,
                                       description='Pyramid:', value=0)
        level_wid.on_trait_change(update_widgets, 'value')
        level_wid.on_trait_change(plot_function, 'value')
        radio_children = [level_wid, mode_wid, mean_wid]
    else:
        radio_children = [mode_wid, mean_wid]
    radio_wids = ContainerWidget(children=radio_children)
    tmp_wid = ContainerWidget(children=[radio_wids, model_parameters_wid])
    wid = TabWidget(children=[tmp_wid, figure_options_wid, info_wid])
    if popup:
        wid = PopupWidget(children=[wid], button_text='Shape Model Menu')

    # display final widget
    display(wid)

    # set final tab titles
    tab_titles = ['Shape parameters', 'Figure options', 'Model info']
    if popup:
        for (k, tl) in enumerate(tab_titles):
            wid.children[0].set_title(k, tl)
    else:
        for (k, tl) in enumerate(tab_titles):
            wid.set_title(k, tl)

    # align widgets
    tmp_wid.remove_class('vbox')
    tmp_wid.add_class('hbox')
    format_model_parameters(model_parameters_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=True)
    format_figure_options(figure_options_wid, container_padding='6px',
                          container_margin='6px',
                          container_border='1px solid black',
                          toggle_button_font_weight='bold',
                          border_visible=False)
    format_info_print(info_wid, font_size_in_pt='9pt', container_padding='6px',
                      container_margin='6px',
                      container_border='1px solid black',
                      toggle_button_font_weight='bold', border_visible=False)

    # update widgets' state for image number 0
    update_widgets('', 0)

    # Reset value to enable initial visualization
    figure_options_wid.children[2].value = False


def visualize_appearance_model(appearance_models, n_parameters=5,
                               parameters_bounds=(-3.0, 3.0),
                               figure_size=(7, 7), mode='multiple',
                               popup=False, **kwargs):
    r"""
    Allows the dynamic visualization of a multilevel appearance model.

    Parameters
    -----------
    appearance_models : `list` of :map:`PCAModel` or subclass
        The multilevel appearance model to be displayed. Note that each level
        can have different attributes, e.g. number of parameters, feature type,
        number of channels.

    n_parameters : `int` or `list` of `int` or None, optional
        The number of principal components to be used for the parameters
        sliders.
        If int, then the number of sliders per level is the minimum between
        n_parameters and the number of active components per level.
        If list of int, then a number of sliders is defined per level.
        If None, all the active components per level will have a slider.

    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.

    figure_size : (`int`, `int`), optional
        The size of the plotted figures.

    mode : 'single' or 'multiple', optional
        If single, only a single slider is constructed along with a drop down
        menu.
        If multiple, a slider is constructed for each parameter.

    popup : `boolean`, optional
        If enabled, the widget will appear as a popup window.

    kwargs : `dict`, optional
        Passed through to the viewer.
    """
    from menpo.image import MaskedImage

    # make sure that appearance_models is a list even with one member
    if not isinstance(appearance_models, list):
        appearance_models = [appearance_models]

    # find number of levels (i.e. number of appearance models)
    n_levels = len(appearance_models)

    # find maximum number of components per level
    max_n_params = [ap.n_active_components for ap in appearance_models]

    # check given n_parameters
    # the returned n_parameters is a list of len n_levels
    n_parameters = _check_n_parameters(n_parameters, n_levels, max_n_params)

    # define plot function
    def plot_function(name, value):
        # get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # get parameters values
        parameters_values = model_parameters_wid.parameters_values

        # compute instance
        weights = parameters_values * appearance_models[level].eigenvalues[:len(parameters_values)] ** 0.5
        instance = appearance_models[level].instance(weights)

        # show image with selected options
        _plot_figure(image=instance,
                     image_enabled=True,
                     landmarks_enabled=landmark_options_wid.landmarks_enabled,
                     image_is_masked=channel_options_wid.image_is_masked,
                     masked_enabled=channel_options_wid.masked_enabled,
                     channels=channel_options_wid.channels,
                     glyph_enabled=channel_options_wid.glyph_enabled,
                     glyph_block_size=channel_options_wid.glyph_block_size,
                     glyph_use_negative=channel_options_wid.glyph_use_negative,
                     sum_enabled=channel_options_wid.sum_enabled,
                     groups=[landmark_options_wid.group],
                     with_labels=[landmark_options_wid.with_labels],
                     groups_colours=dict(),
                     subplots_enabled=False,
                     subplots_titles=dict(),
                     image_axes_mode=True,
                     legend_enabled=landmark_options_wid.legend_enabled,
                     x_scale=figure_options_wid.x_scale,
                     y_scale=figure_options_wid.y_scale,
                     axes_visible=figure_options_wid.axes_visible,
                     figure_size=figure_size,
                     **kwargs)

        # update info text widget
        update_info(instance, level, landmark_options_wid.group)

    # define function that updates info text
    def update_info(image, level, group):
        # prepare channels str
        ch_str = 'channels'
        if image.n_channels == 1:
            ch_str = 'channel'

        # create info str
        txt = "$\\bullet~\\texttt{Level: " + "{}".format(level+1) + \
              " out of " + "{}".format(n_levels) + \
              ".}\\\\ \\bullet~\\texttt{" + \
              "{}".format(appearance_models[level].n_components) + \
              " components in total.}\\\\ \\bullet~\\texttt{" + \
              "{}".format(appearance_models[level].n_active_components) + \
              " active components.}\\\\ \\bullet~\\texttt{" + \
              "{0:.1f}".format(appearance_models[level].variance_ratio*100) + \
              "% variance kept.}\\\\ " \
              "\\bullet~\\texttt{Reference shape of size " + \
              image._str_shape + " with " + \
              "{} {}".format(image.n_channels, ch_str) + \
              ".}\\\\ \\bullet~\\texttt{" + \
              "{}".format(appearance_models[level].n_features) + \
              " features.}\\\\ \\bullet~\\texttt{" + \
              "{}".format(image.landmarks[group].lms.n_points) + \
              " landmark points.}\\\\ \\bullet~\\texttt{Instance: min=" + \
              "{0:.3f}".format(image.pixels.min()) + \
              ", max=" + "{0:.3f}".format(image.pixels.max()) + "}$"

        # update info widget text
        info_wid.children[1].value = txt

    # Plot eigenvalues function
    def plot_eigenvalues(name):
        # get parameters
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # show eigenvalues plots
        _plot_eigenvalues(appearance_models[level], figure_size,
                          figure_options_wid.x_scale,
                          figure_options_wid.y_scale)

    # create options widgets
    model_parameters_wid = model_parameters(n_parameters[0], plot_function,
                                            params_str='param ', mode=mode,
                                            params_bounds=parameters_bounds,
                                            toggle_show_default=True,
                                            toggle_show_visible=False,
                                            plot_eig_visible=True,
                                            plot_eig_function=plot_eigenvalues)
    channel_options_wid = channel_options(appearance_models[0].mean.n_channels,
                                          isinstance(appearance_models[0].mean,
                                                     MaskedImage),
                                          plot_function, masked_default=True,
                                          toggle_show_default=True,
                                          toggle_show_visible=False)
    all_groups_keys, all_labels_keys = \
        _extract_groups_labels(appearance_models[0].mean)
    landmark_options_wid = landmark_options(all_groups_keys, all_labels_keys,
                                            plot_function,
                                            toggle_show_default=True,
                                            landmarks_default=True,
                                            legend_default=False,
                                            toggle_show_visible=False)
    figure_options_wid = figure_options(plot_function, scale_default=1.,
                                        show_axes_default=True,
                                        toggle_show_default=True,
                                        toggle_show_visible=False)
    info_wid = info_print(toggle_show_default=True, toggle_show_visible=False)

    # define function that updates options' widgets state
    def update_widgets(name, value):
        # update model parameters
        update_model_parameters(model_parameters_wid, n_parameters[value],
                                plot_function, params_str='param ')
        # update channel options
        update_channel_options(channel_options_wid,
                               appearance_models[value].mean.n_channels,
                               isinstance(appearance_models[0].mean,
                                          MaskedImage))

    # create final widget
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = RadioButtonsWidget(values=radio_str,
                                       description='Pyramid:', value=0)
        level_wid.on_trait_change(update_widgets, 'value')
        level_wid.on_trait_change(plot_function, 'value')
        tmp_children.insert(0, level_wid)
    tmp_wid = ContainerWidget(children=tmp_children)
    wid = TabWidget(children=[tmp_wid, channel_options_wid,
                              landmark_options_wid, figure_options_wid,
                              info_wid])
    if popup:
        wid = PopupWidget(children=[wid], button_text='Appearance Model Menu')

    # display final widget
    display(wid)

    # set final tab titles
    tab_titles = ['Appearance parameters', 'Channels options',
                  'Landmarks options', 'Figure options', 'Model info']
    if popup:
        for (k, tl) in enumerate(tab_titles):
            wid.children[0].set_title(k, tl)
    else:
        for (k, tl) in enumerate(tab_titles):
            wid.set_title(k, tl)

    # align widgets
    tmp_wid.remove_class('vbox')
    tmp_wid.add_class('hbox')
    format_model_parameters(model_parameters_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=True)
    format_channel_options(channel_options_wid, container_padding='6px',
                           container_margin='6px',
                           container_border='1px solid black',
                           toggle_button_font_weight='bold',
                           border_visible=False)
    format_landmark_options(landmark_options_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=False)
    format_figure_options(figure_options_wid, container_padding='6px',
                          container_margin='6px',
                          container_border='1px solid black',
                          toggle_button_font_weight='bold',
                          border_visible=False)
    format_info_print(info_wid, font_size_in_pt='9pt', container_padding='6px',
                      container_margin='6px',
                      container_border='1px solid black',
                      toggle_button_font_weight='bold', border_visible=False)

    # update widgets' state for level 0
    update_widgets('', 0)

    # Reset value to enable initial visualization
    figure_options_wid.children[2].value = False


def visualize_aam(aam, n_shape_parameters=5, n_appearance_parameters=5,
                  parameters_bounds=(-3.0, 3.0), figure_size=(7, 7),
                  mode='multiple', popup=False, **kwargs):
    r"""
    Allows the dynamic visualization of a multilevel AAM.

    Parameters
    -----------
    aam : :map:`AAM` or subclass
        The multilevel AAM to be displayed. Note that each level can have
        different attributes, e.g. number of active components, feature type,
        number of channels.

    n_shape_parameters : `int` or `list` of `int` or None, optional
        The number of shape principal components to be used for the parameters
        sliders.
        If int, then the number of sliders per level is the minimum between
        n_parameters and the number of active components per level.
        If list of int, then a number of sliders is defined per level.
        If None, all the active components per level will have a slider.

    n_appearance_parameters : `int` or `list` of `int` or None, optional
        The number of appearance principal components to be used for the
        parameters sliders.
        If int, then the number of sliders per level is the minimum between
        n_parameters and the number of active components per level.
        If list of int, then a number of sliders is defined per level.
        If None, all the active components per level will have a slider.

    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.

    figure_size : (`int`, `int`), optional
        The size of the plotted figures.

    mode : 'single' or 'multiple', optional
        If single, only a single slider is constructed along with a drop down
        menu.
        If multiple, a slider is constructed for each parameter.

    popup : `boolean`, optional
        If enabled, the widget will appear as a popup window.

    kwargs : `dict`, optional
        Passed through to the viewer.
    """
    from menpo.image import MaskedImage

    # find number of levels
    n_levels = aam.n_levels

    # find maximum number of components per level
    max_n_shape = [sp.n_active_components for sp in aam.shape_models]
    max_n_appearance = [ap.n_active_components for ap in aam.appearance_models]

    # check given n_parameters
    # the returned n_parameters is a list of len n_levels
    n_shape_parameters = _check_n_parameters(n_shape_parameters, n_levels,
                                             max_n_shape)
    n_appearance_parameters = _check_n_parameters(n_appearance_parameters,
                                                  n_levels, max_n_appearance)

    # define plot function
    def plot_function(name, value):
        # get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # get weights and compute instance
        shape_weights = shape_model_parameters_wid.parameters_values
        appearance_weights = appearance_model_parameters_wid.parameters_values
        instance = aam.instance(level=level, shape_weights=shape_weights,
                                appearance_weights=appearance_weights)

        # show image with selected options
        _plot_figure(image=instance,
                     image_enabled=True,
                     landmarks_enabled=landmark_options_wid.landmarks_enabled,
                     image_is_masked=channel_options_wid.image_is_masked,
                     masked_enabled=channel_options_wid.masked_enabled,
                     channels=channel_options_wid.channels,
                     glyph_enabled=channel_options_wid.glyph_enabled,
                     glyph_block_size=channel_options_wid.glyph_block_size,
                     glyph_use_negative=channel_options_wid.glyph_use_negative,
                     sum_enabled=channel_options_wid.sum_enabled,
                     groups=[landmark_options_wid.group],
                     with_labels=[landmark_options_wid.with_labels],
                     groups_colours=dict(),
                     subplots_enabled=False,
                     subplots_titles=dict(),
                     image_axes_mode=True,
                     legend_enabled=landmark_options_wid.legend_enabled,
                     x_scale=figure_options_wid.x_scale,
                     y_scale=figure_options_wid.y_scale,
                     axes_visible=figure_options_wid.axes_visible,
                     figure_size=figure_size,
                     **kwargs)

        # update info text widget
        update_info(aam, instance, level, landmark_options_wid.group)

    # define function that updates info text
    def update_info(aam, instance, level, group):
        # features info
        from menpo.fitmultilevel.base import name_of_callable
        if aam.appearance_models[level].mean.n_channels == 1:
            if aam.pyramid_on_features:
                tmp_feat = "Feature is {} with 1 channel.".\
                    format(name_of_callable(aam.features))
            else:
                tmp_feat = "Feature is {} with 1 channel.".\
                    format(name_of_callable(aam.features[level]))
        else:
            if aam.pyramid_on_features:
                tmp_feat = "Feature is {} with {} channel.".\
                    format(name_of_callable(aam.features),
                           aam.appearance_models[level].mean.n_channels)
            else:
                tmp_feat = "Feature is {} with {} channel.".\
                    format(name_of_callable(aam.features[level]),
                           aam.appearance_models[level].mean.n_channels)
        # create info str
        if n_levels > 1:
            # shape models info
            if aam.scaled_shape_models:
                tmp_shape_models = "Each level has a scaled shape model " \
                                   "(reference frame)."
            else:
                tmp_shape_models = "Shape models (reference frames) are " \
                                   "not scaled."

            # pyramid info
            if aam.pyramid_on_features:
                tmp_pyramid = "Pyramid was applied on feature space."
            else:
                tmp_pyramid = "Features were extracted at each pyramid level."

            txt = "$\\bullet~\\texttt{" + "{}".format(aam.n_training_images) + \
                  " training images.}" + \
                  "\\\\ \\bullet~\\texttt{Warp using " + \
                  aam.transform.__name__ + \
                  " transform.} \\\\ \\bullet~\\texttt{Level " + \
                  "{}/{}".format(level+1, aam.n_levels) + " (downscale=" + \
                  "{0:.1f}".format(aam.downscale) + ").}" + \
                  "\\\\ \\bullet~\\texttt{" + tmp_shape_models + "}" + \
                  "\\\\ \\bullet~\\texttt{" + tmp_pyramid + \
                  "}\\\\ \\bullet~\\texttt{" + tmp_feat + \
                  "}\\\\ \\bullet~\\texttt{Reference frame of length " + \
                  "{} ({} x {}C, {} x {}C).".format(
                      aam.appearance_models[level].n_features,
                      aam.appearance_models[level].template_instance.n_true_pixels,
                      aam.appearance_models[level].mean.n_channels,
                      aam.appearance_models[level].template_instance._str_shape,
                      aam.appearance_models[level].mean.n_channels) + \
                  "}\\\\ \\bullet~\\texttt{" + \
                  "{0} shape components ({1:.2f}% of variance).".format(
                      aam.shape_models[level].n_components,
                      aam.shape_models[level].variance_ratio * 100) + \
                  "}\\\\ \\bullet~\\texttt{" + \
                  "{0} appearance components ({1:.2f}% of variance).".format(
                      aam.appearance_models[level].n_components,
                      aam.appearance_models[level].variance_ratio * 100) + \
                  "}\\\\ \\bullet~\\texttt{" + \
                  "{}".format(instance.landmarks[group].lms.n_points) + \
                  " landmark points.}\\\\ \\bullet~\\texttt{Instance: min=" + \
                  "{0:.3f}".format(instance.pixels.min()) + ", max=" + \
                  "{0:.3f}".format(instance.pixels.max()) + "}$"
        else:
            txt = "$\\bullet~\\texttt{" + "{}".format(aam.n_training_images) + \
                  " training images.}\\\\ \\bullet~\\texttt{Warp using " + \
                  aam.transform.__name__ + " transform with '" + \
                  aam.interpolator + "' interpolation.}" + \
                  "\\\\ \\bullet~\\texttt{" + tmp_feat + \
                  "}\\\\ \\bullet~\\texttt{Reference frame of length " + \
                  "{} ({} x {}C, {} x {}C).".format(
                      aam.appearance_models[level].n_features,
                      aam.appearance_models[level].template_instance.n_true_pixels,
                      aam.appearance_models[level].mean.n_channels,
                      aam.appearance_models[level].template_instance._str_shape,
                      aam.appearance_models[level].mean.n_channels) + \
                  "}\\\\ \\bullet~\\texttt{" + \
                  "{0} shape components ({1:.2f}% of variance).".format(
                      aam.shape_models[level].n_components,
                      aam.shape_models[level].variance_ratio * 100) + \
                  "}\\\\ \\bullet~\\texttt{" + \
                  "{0} appearance components ({1:.2f}% of variance).".format(
                      aam.appearance_models[level].n_components,
                      aam.appearance_models[level].variance_ratio * 100) + \
                  "}\\\\ \\bullet~\\texttt{" + \
                  "{}".format(instance.landmarks[group].lms.n_points) + \
                  " landmark points.}\\\\ \\bullet~\\texttt{Instance: min=" + \
                  "{0:.3f}".format(instance.pixels.min()) + ", max=" + \
                  "{0:.3f}".format(instance.pixels.max()) + "}$"
        info_wid.children[1].value = txt

    # Plot shape eigenvalues function
    def plot_shape_eigenvalues(name):
        # get parameters
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # show eigenvalues plots
        _plot_eigenvalues(aam.shape_models[level], figure_size,
                          figure_options_wid.x_scale,
                          figure_options_wid.y_scale)

    # Plot appearance eigenvalues function
    def plot_appearance_eigenvalues(name):
        # get parameters
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # show eigenvalues plots
        _plot_eigenvalues(aam.appearance_models[level], figure_size,
                          figure_options_wid.x_scale,
                          figure_options_wid.y_scale)

    # create options widgets
    shape_model_parameters_wid = model_parameters(
        n_shape_parameters[0], plot_function, params_str='param ', mode=mode,
        params_bounds=parameters_bounds, toggle_show_default=False,
        toggle_show_visible=True, toggle_show_name='Shape Parameters',
        plot_eig_visible=True, plot_eig_function=plot_shape_eigenvalues)
    appearance_model_parameters_wid = model_parameters(
        n_appearance_parameters[0], plot_function, params_str='param ',
        mode=mode, params_bounds=parameters_bounds, toggle_show_default=False,
        toggle_show_visible=True, toggle_show_name='Appearance Parameters',
        plot_eig_visible=True, plot_eig_function=plot_appearance_eigenvalues)
    channel_options_wid = channel_options(
        aam.appearance_models[0].mean.n_channels,
        isinstance(aam.appearance_models[0].mean, MaskedImage), plot_function,
        masked_default=True, toggle_show_default=True,
        toggle_show_visible=False)
    all_groups_keys, all_labels_keys = \
        _extract_groups_labels(aam.appearance_models[0].mean)
    landmark_options_wid = landmark_options(all_groups_keys, all_labels_keys,
                                            plot_function,
                                            toggle_show_default=True,
                                            landmarks_default=True,
                                            legend_default=False,
                                            toggle_show_visible=False)
    figure_options_wid = figure_options(plot_function, scale_default=1.,
                                        show_axes_default=True,
                                        toggle_show_default=True,
                                        toggle_show_visible=False)
    info_wid = info_print(toggle_show_default=True, toggle_show_visible=False)

    # define function that updates options' widgets state
    def update_widgets(name, value):
        # update shape model parameters
        update_model_parameters(shape_model_parameters_wid,
                                n_shape_parameters[value],
                                plot_function, params_str='param ')
        # update appearance model parameters
        update_model_parameters(appearance_model_parameters_wid,
                                n_appearance_parameters[value],
                                plot_function, params_str='param ')
        # update channel options
        update_channel_options(channel_options_wid,
                               aam.appearance_models[value].mean.n_channels,
                               isinstance(aam.appearance_models[0].mean,
                                          MaskedImage))

    # create final widget
    model_parameters_wid = ContainerWidget(
        children=[shape_model_parameters_wid, appearance_model_parameters_wid])
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = RadioButtonsWidget(values=radio_str,
                                       description='Pyramid:', value=0)
        level_wid.on_trait_change(update_widgets, 'value')
        level_wid.on_trait_change(plot_function, 'value')
        tmp_children.insert(0, level_wid)
    tmp_wid = ContainerWidget(children=tmp_children)
    wid = TabWidget(children=[tmp_wid, channel_options_wid,
                              landmark_options_wid, figure_options_wid,
                              info_wid])
    if popup:
        wid = PopupWidget(children=[wid], button_text='AAM Menu')

    # display final widget
    display(wid)

    # set final tab titles
    tab_titles = ['AAM parameters', 'Channels options', 'Landmarks options',
                  'Figure options', 'Model info']
    if popup:
        for (k, tl) in enumerate(tab_titles):
            wid.children[0].set_title(k, tl)
    else:
        for (k, tl) in enumerate(tab_titles):
            wid.set_title(k, tl)

    # align widgets
    if n_levels > 1:
        tmp_wid.remove_class('vbox')
        tmp_wid.add_class('hbox')
    format_model_parameters(shape_model_parameters_wid,
                            container_padding='6px', container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=True)
    format_model_parameters(appearance_model_parameters_wid,
                            container_padding='6px', container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=True)
    format_channel_options(channel_options_wid, container_padding='6px',
                           container_margin='6px',
                           container_border='1px solid black',
                           toggle_button_font_weight='bold',
                           border_visible=False)
    format_landmark_options(landmark_options_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=False)
    format_figure_options(figure_options_wid, container_padding='6px',
                          container_margin='6px',
                          container_border='1px solid black',
                          toggle_button_font_weight='bold',
                          border_visible=False)
    format_info_print(info_wid, font_size_in_pt='9pt', container_padding='6px',
                      container_margin='6px',
                      container_border='1px solid black',
                      toggle_button_font_weight='bold', border_visible=False)

    # update widgets' state for level 0
    update_widgets('', 0)

    # Reset value to enable initial visualization
    figure_options_wid.children[2].value = False


def visualize_fitting_results(fitting_results, figure_size=(7, 7), popup=False,
                              **kwargs):
    r"""
    Widget that allows browsing through a list of fitting results.

    Parameters
    -----------
    fitting_results : `list` of :map:`FittingResult` or subclass
        The list of fitting results to be displayed. Note that the fitting
        results can have different attributes between them, i.e. different
        number of iterations, number of channels etc.

    figure_size : (`int`, `int`), optional
        The initial size of the plotted figures.

    popup : `boolean`, optional
        If enabled, the widget will appear as a popup window.

    kwargs : `dict`, optional
        Passed through to the viewer.
    """
    from menpo.image import MaskedImage

    # make sure that fitting_results is a list even with one fitting_result
    if not isinstance(fitting_results, list):
        fitting_results = [fitting_results]

    # find number of fitting_results
    n_fitting_results = len(fitting_results)

    # create dictionaries
    iter_str = 'iter_'
    groups_final_dict = dict()
    colour_final_dict = dict()
    groups_final_dict['initial'] = 'Initial shape'
    colour_final_dict['initial'] = 'r'
    groups_final_dict['final'] = 'Final shape'
    colour_final_dict['final'] = 'b'
    groups_final_dict['ground'] = 'Ground-truth shape'
    colour_final_dict['ground'] = 'y'

    # define function that plots errors curve
    def plot_errors_function(name):
        # clear current figure
        clear_output(wait=True)

        # get selected image
        im = 0
        if n_fitting_results > 1:
            im = image_number_wid.selected_index

        # plot errors curve
        plt.plot(range(len(fitting_results[im].errors())),
                 fitting_results[im].errors(), '-bo')
        plt.gca().set_xlim(0, len(fitting_results[im].errors())-1)
        plt.xlabel('Iteration')
        plt.ylabel('Fitting Error')
        plt.title("Fitting error evolution of Image {}".format(im))
        plt.grid("on")

        # set figure size
        x_scale = figure_options_wid.x_scale
        y_scale = figure_options_wid.y_scale
        plt.gcf().set_size_inches([x_scale, y_scale] * np.asarray(figure_size))

    # define function that plots displacements curve
    def plot_displacements_function(name):
        # clear current figure
        clear_output(wait=True)

        # get selected image
        im = 0
        if n_fitting_results > 1:
            im = image_number_wid.selected_index

        # plot errors curve
        plt.plot(range(len(fitting_results[im].errors())),
                 fitting_results[im].errors(), '-bo')
        plt.gca().set_xlim(0, len(fitting_results[im].errors())-1)
        plt.xlabel('Iteration')
        plt.ylabel('Fitting Error')
        plt.title("Fitting error evolution of Image {}".format(im))
        plt.grid("on")

        # set figure size
        x_scale = figure_options_wid.x_scale
        y_scale = figure_options_wid.y_scale
        plt.gcf().set_size_inches([x_scale, y_scale] * np.asarray(figure_size))

    # define plot function
    def plot_function(name, value):
        # get selected image
        im = 0
        if n_fitting_results > 1:
            im = image_number_wid.selected_index

        # selected mode: final or iterations
        final_enabled = False
        if result_wid.selected_index == 0:
            final_enabled = True

        # update info text widget
        update_info('', error_rype_wid.value)

        # call helper _plot_figure
        if final_enabled:
            _plot_figure(image=fitting_results[im].fitted_image,
                         image_enabled=final_result_wid.show_image,
                         landmarks_enabled=True,
                         image_is_masked=False,
                         masked_enabled=False,
                         channels=channel_options_wid.channels,
                         glyph_enabled=channel_options_wid.glyph_enabled,
                         glyph_block_size=channel_options_wid.glyph_block_size,
                         glyph_use_negative=channel_options_wid.glyph_use_negative,
                         sum_enabled=channel_options_wid.sum_enabled,
                         groups=final_result_wid.groups,
                         with_labels=[None] * len(final_result_wid.groups),
                         groups_colours=colour_final_dict,
                         subplots_enabled=final_result_wid.subplots_enabled,
                         subplots_titles=groups_final_dict,
                         image_axes_mode=True,
                         legend_enabled=final_result_wid.legend_enabled,
                         x_scale=figure_options_wid.x_scale,
                         y_scale=figure_options_wid.y_scale,
                         axes_visible=figure_options_wid.axes_visible,
                         figure_size=figure_size,
                         **kwargs)
        else:
            # create subplot titles dict and colours dict
            groups_dict = dict()
            colour_dict = dict()
            cols = np.random.random([3, len(iterations_wid.groups)])
            for i, group in enumerate(iterations_wid.groups):
                iter_num = group[len(iter_str)::]
                groups_dict[iter_str + iter_num] = "Iteration " + iter_num
                colour_dict[iter_str + iter_num] = cols[:, i]

            # plot
            _plot_figure(image=fitting_results[im].iter_image,
                         image_enabled=iterations_wid.show_image,
                         landmarks_enabled=True,
                         image_is_masked=False,
                         masked_enabled=False,
                         channels=channel_options_wid.channels,
                         glyph_enabled=channel_options_wid.glyph_enabled,
                         glyph_block_size=channel_options_wid.glyph_block_size,
                         glyph_use_negative=channel_options_wid.glyph_use_negative,
                         sum_enabled=channel_options_wid.sum_enabled,
                         groups=iterations_wid.groups,
                         with_labels=[None] * len(iterations_wid.groups),
                         groups_colours=colour_dict,
                         subplots_enabled=iterations_wid.subplots_enabled,
                         subplots_titles=groups_dict,
                         image_axes_mode=True,
                         legend_enabled=iterations_wid.legend_enabled,
                         x_scale=figure_options_wid.x_scale,
                         y_scale=figure_options_wid.y_scale,
                         axes_visible=figure_options_wid.axes_visible,
                         figure_size=figure_size,
                         **kwargs)

    # define function that updates info text
    def update_info(name, value):
        # get selected image
        im = 0
        if n_fitting_results > 1:
            im = image_number_wid.selected_index

        # create output str
        txt = "$\\bullet~\\texttt{Initial error: " + \
              "{0:.4f}".format(fitting_results[im].initial_error(error_type=
                                                                 value)) + \
              "}\\\\ \\bullet~\\texttt{Final error: " + \
              "{0:.4f}".format(fitting_results[im].final_error(error_type=
                                                               value)) + \
              "}\\\\ \\bullet~\\texttt{" + \
              "{}".format(fitting_results[im].n_iters) + \
              " iterations.}\\\\ \\bullet~\\texttt{" + \
              "{0} levels with downscale of {1:.1f}".format(
                  fitting_results[im].n_levels,
                  fitting_results[im].downscale) + \
              "}.$"
        info_wid.children[1].value = txt

    # Create options widgets
    channel_options_wid = channel_options(
        fitting_results[0].fitted_image.n_channels,
        isinstance(fitting_results[0].fitted_image, MaskedImage), plot_function,
        masked_default=False, toggle_show_default=True,
        toggle_show_visible=False)
    figure_options_wid = figure_options(plot_function, scale_default=1.,
                                        show_axes_default=True,
                                        toggle_show_default=True,
                                        toggle_show_visible=False)
    info_wid = info_print(toggle_show_default=True, toggle_show_visible=False)

    # Create landmark groups checkboxes
    all_groups_keys, all_labels_keys = _extract_groups_labels(
        fitting_results[0].fitted_image)
    final_result_wid = final_result_options(all_groups_keys, plot_function,
                                            title='Final',
                                            show_image_default=True,
                                            subplots_enabled_default=True,
                                            legend_default=True,
                                            toggle_show_default=True,
                                            toggle_show_visible=False)
    iterations_wid = iterations_result_options(
        fitting_results[0].n_iters, not fitting_results[0].gt_shape is None,
        fitting_results[0].fitted_image.landmarks['final'].lms.n_points,
        plot_function, plot_errors_function, plot_displacements_function,
        iter_str=iter_str, title='Iterations', show_image_default=True,
        subplots_enabled_default=False, legend_default=True,
        toggle_show_default=True, toggle_show_visible=False)
    iterations_wid.children[2].children[3].on_click(plot_errors_function)
    iterations_wid.children[2].children[4].children[0].on_click(
        plot_displacements_function)

    # Create error type radio buttons
    error_type_values = OrderedDict()
    error_type_values['Point-to-point Normalized Mean Error'] = 'me_norm'
    error_type_values['Point-to-point Mean Error'] = 'me'
    error_type_values['RMS Error'] = 'rmse'
    error_rype_wid = RadioButtonsWidget(values=error_type_values,
                                        value='me_norm',
                                        description='Error type')
    error_rype_wid.on_trait_change(update_info, 'value')

    # define function that updates options' widgets state
    def update_widgets(name, value):
        # get new groups and labels, update landmark options and format them
        group_keys, labels_keys = _extract_groups_labels(
            fitting_results[value].fitted_image)
        # update channel options
        update_channel_options(
            channel_options_wid,
            n_channels=fitting_results[value].fitted_image.n_channels,
            image_is_masked=isinstance(fitting_results[value].fitted_image,
                                       MaskedImage))
        # update final result's options
        update_final_result_options(final_result_wid, group_keys, plot_function)
        # update iterations result's options
        update_iterations_result_options(
            iterations_wid, fitting_results[value].n_iters,
            not fitting_results[value].gt_shape is None,
            fitting_results[value].fitted_image.landmarks['final'].lms.n_points,
            iter_str=iter_str)

    # define function that combines the results' tab widget with the animation
    # If animation is activated and the user selects the iterations tab, then
    # the animation stops.
    def results_tab_fun(name, value):
        if (value == 1 and
                image_number_wid.children[1].children[1].children[0].children[0].value):
            image_number_wid.children[1].children[1].children[0].children[1].\
                value = True

    # Create final widget
    options_wid = TabWidget(children=[channel_options_wid, figure_options_wid,
                                      error_rype_wid])
    result_wid = TabWidget(children=[final_result_wid, iterations_wid])
    result_wid.on_trait_change(results_tab_fun, 'selected_index')
    result_wid.on_trait_change(plot_function, 'selected_index')
    if n_fitting_results > 1:
        # image selection slider
        image_number_wid = animation_options(
            index_min_val=0, index_max_val=n_fitting_results-1,
            plot_function=plot_function, update_function=update_widgets,
            index_step=1, index_default=0,
            index_description='Image Number', index_minus_description='<',
            index_plus_description='>', index_style='buttons',
            index_text_editable=True, loop_default=True, interval_default=0.3,
            toggle_show_title='Image Options', toggle_show_default=True,
            toggle_show_visible=False)

        # final widget
        tab_wid = TabWidget(children=[info_wid, result_wid, options_wid])
        wid = ContainerWidget(children=[image_number_wid, tab_wid])
        tab_titles = ['Info', 'Result', 'Options']
        button_title = 'Fitting Results Menu'
    else:
        # final widget
        wid = TabWidget(children=[info_wid, result_wid, options_wid])
        tab_titles = ['Image info', 'Result', 'Options']
        button_title = 'Fitting Result Menu'
    # create popup widget if asked
    if popup:
        wid = PopupWidget(children=[wid], button_text=button_title)

    # display final widget
    display(wid)

    # set final tab titles
    if popup:
        if n_fitting_results > 1:
            for (k, tl) in enumerate(tab_titles):
                wid.children[0].children[1].set_title(k, tl)
        else:
            for (k, tl) in enumerate(tab_titles):
                wid.children[0].set_title(k, tl)
    else:
        if n_fitting_results > 1:
            for (k, tl) in enumerate(tab_titles):
                wid.children[1].set_title(k, tl)
        else:
            for (k, tl) in enumerate(tab_titles):
                wid.set_title(k, tl)
    result_wid.set_title(0, 'Final Fitting')
    result_wid.set_title(1, 'Iterations')
    options_wid.set_title(0, 'Channels')
    options_wid.set_title(1, 'Figure')
    options_wid.set_title(2, 'Error Type')

    # format options' widgets
    if n_fitting_results > 1:
        format_animation_options(image_number_wid, index_text_width='0.5cm',
                                 container_padding='6px',
                                 container_margin='6px',
                                 container_border='1px solid black',
                                 toggle_button_font_weight='bold',
                                 border_visible=False)
    format_channel_options(channel_options_wid, container_padding='6px',
                           container_margin='6px',
                           container_border='1px solid black',
                           toggle_button_font_weight='bold',
                           border_visible=False)
    format_figure_options(figure_options_wid, container_padding='6px',
                          container_margin='6px',
                          container_border='1px solid black',
                          toggle_button_font_weight='bold',
                          border_visible=False)
    format_info_print(info_wid, font_size_in_pt='9pt', container_padding='6px',
                      container_margin='6px',
                      container_border='1px solid black',
                      toggle_button_font_weight='bold', border_visible=False)
    format_final_result_options(final_result_wid, container_padding='6px',
                                container_margin='6px',
                                container_border='1px solid black',
                                toggle_button_font_weight='bold',
                                border_visible=False)
    format_iterations_result_options(iterations_wid, container_padding='6px',
                                     container_margin='6px',
                                     container_border='1px solid black',
                                     toggle_button_font_weight='bold',
                                     border_visible=False)

    # Reset value to enable initial visualization
    figure_options_wid.children[2].value = False


def plot_ced(final_errors, x_axis=None, initial_errors=None, title=None,
             x_label=None, y_label=None, legend=None, colors=None,
             markers=None, plot_size=(14, 7)):
    r"""
    Plots the Cumulative Error Distribution (CED) graph given a list of
    final fitting errors, or a list of lists containing final fitting errors.

    Parameters
    -----------
    final_errors : `list` of `floats` or `list` of `list` of `floats`
        The list of final errors or a list containing a list of
        final fitting errors.

        .. note::
        Using Menpo's fitting framework, the typical way to obtain a
        list of final errors is to append calls to the method
        ``final_error()`` on several fitting result objects:

            ``final_errors = [fr.final_error() for fr in fitting_results]``

        where ``fitting_results`` is a `list` of :map:`FittingResult`
        objects.

    x_axis : `list` of `float`, optional
        The x axis to be used.

    initial_errors : `list` of `floats`, optional.
        The list of initial fitting errors.

        .. note::
        Using Menpo's fitting framework, the typical way to obtain a
        list of initial errors is to append calls to the method
        ``initial_error()`` on several fitting result objects:

            ``initial_errors = [fr.initial_error() for fr in fitting_results]``

        where ``fitting_results`` is a `list` of :map:`FittingResult`
        objects.

    title : `str`, optional
        The figure title.

    x_label : `str`, optional
        The label associated to the x axis.

    y_label : `str`, optional
        The label associated to the y axis.

    legend : `str` or `list` of `str`, optional

    colors : `matplotlib color` or `list` of `matplotlib color`, optional
        The color of the line to be plotted.

    markers : `matplotlib marker` or `list` of `matplotlib marker`, optional
        The marker of the line to be plotted.

    figure_size : (`int`, `int`), optional
        The size of the plotted figures.

    figure_scales : (`float`, `float`), optional
        The range of scales that can be optionally applied to the figure.

    kwargs : `dict`, optional
        Passed through to the viewer.
    """
    from menpo.fitmultilevel.functions import compute_cumulative_error

    if type(final_errors[0]) != list:
        # if final_errors is not a list of lists, turn it into list of lists
        final_errors = [final_errors]

    if title is None:
        title = 'Cumulative error distribution'
    if x_label is None:
        x_label = 'Error'
    if y_label is None:
        y_label = 'Proportion of images'

    if colors is None:
        # color are chosen at random
        colors = [np.random.random((3,)) for _ in range(len(final_errors))]
    elif len(colors) == 1 and len(final_errors) > 1:
        colors = [colors[0] for _ in range(len(final_errors))]
    elif len(colors) != len(final_errors):
        raise ValueError('colors must be...'.format())

    if markers is None:
        # markers default to square
        markers = ['s' for _ in range(len(final_errors))]
    elif len(markers) == 1 and len(final_errors) > 1:
        markers = [markers[0] for _ in range(len(final_errors))]
    elif len(markers) != len(final_errors):
        raise ValueError('markers must be...'.format())

    if legend is None:
        length = len(final_errors)
        if initial_errors:
            length += 1
        # number based legend
        legend = [str(j) for j in range(length)]
    else:
        if initial_errors:
            if len(legend) != len(final_errors)+1:
                raise ValueError('legend must be...'.format())
        else:
            if len(legend) != len(final_errors):
                raise ValueError('legend must be...'.format())

    if x_axis is None:
        # assume final_errors are computed using norm_me
        x_axis = np.arange(0, 0.101, 0.005)

    if initial_errors:
        # compute cumulative error for the initial errors
        initial_cumulative_error = compute_cumulative_error(initial_errors,
                                                            x_axis)

    # compute cumulative errors
    final_cumulative_errors = [compute_cumulative_error(e, x_axis)
                               for e in final_errors]

    def plot_graph(x_limit):

        if initial_errors:
            plt.plot(x_axis, initial_cumulative_error,
                     color='black',  marker='*')

        for fce, c, m in zip(final_cumulative_errors, colors, markers):
            plt.plot(x_axis, fce, color=c,  marker=m)

        plt.grid(True)
        ax = plt.gca()

        plt.title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        plt.legend(legend, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        plt.xlim([0, x_limit])

        plt.gcf().set_size_inches(plot_size)

    interact(plot_graph, x_limit=(0.0, x_axis[-1], 0.001))


def _plot_figure(image, image_enabled, landmarks_enabled, image_is_masked,
                 masked_enabled, channels, glyph_enabled, glyph_block_size,
                 glyph_use_negative, sum_enabled, groups, with_labels,
                 groups_colours, subplots_enabled, subplots_titles,
                 image_axes_mode, legend_enabled, x_scale, y_scale,
                 axes_visible, figure_size, **kwargs):
    r"""
    Helper function that plots an object given a set of selected options.

    Parameters
    -----------
    image : :map:`Image` or subclass
       The image to be displayed.

    image_enabled : `boolean`
        Flag that determines whether to display the image.

    landmarks_enabled : `boolean`
        Flag that determines whether to display the landmarks.

    image_is_masked : `boolean`
        If True, image is an instance of :map:`MaskedImage`.
        If False, image is an instance of :map:`Image`.

    masked_enabled : `boolean`
        If True and the image is an instance of :map:`MaskedImage`, then only
        the masked pixels will be displayed.

    channels : `int` or `list` of `int`
        The image channels to be displayed.

    glyph_enabled : `boolean`
        Defines whether to display the image as glyph or not.

    glyph_block_size : `int`
        The size of the glyph's blocks.

    glyph_use_negative : `boolean`
        Whether to use the negative hist values.

    sum_enabled : `boolean`
        If true, the image will be displayed as glyph with glyph_block_size=1,
        thus the sum of the image's selected channels.

    groups : `list` of `str`
        A list of the landmark groups to be displayed.

    with_labels : `list` of `list` of `str`
        The labels to be displayed for each group in groups.

    groups_colours : `dict` of `str`
        A dictionary that defines a colour for each of the groups, e.g.
        subplots_titles[groups[0]] = 'b'
        subplots_titles[groups[1]] = 'r'

    subplots_enabled : `boolean`
        Flag that determines whether to plot all selected landmark groups in a
        single axes object or in subplots.

    subplots_titles : `dict` of `str`
        A dictionary that defines a subplot title for each of the groups, e.g.
        subplots_titles[groups[0]] = 'first group'
        subplots_titles[groups[1]] = 'second group'

    image_axes_mode : `boolean`
        If True, then the point clouds are plotted with the axes in the image
        mode.

    legend_enabled : `boolean`
        Flag that determines whether to show the legend for the landmarks.
        If True, it also prints the landmark points' numbers.

    x_scale : `float`
        The scale of x axis.

    y_scale : `float`
        The scale of y axis.

    axes_visible : `boolean`
        If False, the figure's axes will be invisible.

    figure_size : (`int`, `int`)
        The size of the plotted figures.

    kwargs : `dict`, optional
        Passed through to the viewer.
    """
    global glyph
    if glyph is None:
        from menpo.visualize.image import glyph
    # clear current figure, but wait until the new date to be displayed are
    # generated
    clear_output(wait=True)

    # plot
    if image_enabled:
        # image will be displayed
        if landmarks_enabled and len(groups) > 0:
            # there are selected landmark groups and they will be displayed
            if subplots_enabled:
                # calculate subplots structure
                subplots = MatplotlibSubplots()._subplot_layout(len(groups))
            # show image with landmarks
            for k, group in enumerate(groups):
                if subplots_enabled:
                    # create subplot
                    plt.subplot(subplots[0], subplots[1], k + 1)
                    if legend_enabled:
                        # set subplot's title
                        plt.title(subplots_titles[group])
                    if not axes_visible:
                        # turn axes on/off
                        plt.axis('off')
                if image_is_masked:
                    if glyph_enabled or sum_enabled:
                        # image, landmarks, masked, glyph
                        glyph(image, vectors_block_size=glyph_block_size,
                              use_negative=glyph_use_negative,
                              channels=channels).\
                            view_landmarks(masked=masked_enabled,
                                           group_label=group,
                                           with_labels=with_labels[k],
                                           render_labels=(legend_enabled and
                                                          not subplots_enabled),
                                           **kwargs)
                    else:
                        # image, landmarks, masked, not glyph
                        image.view_landmarks(masked=masked_enabled,
                                             group_label=group,
                                             with_labels=with_labels[k],
                                             render_labels=(legend_enabled and
                                                            not subplots_enabled),
                                             channels=channels, **kwargs)
                else:
                    if glyph_enabled or sum_enabled:
                        # image, landmarks, not masked, glyph
                        glyph(image, vectors_block_size=glyph_block_size,
                              use_negative=glyph_use_negative,
                              channels=channels).\
                            view_landmarks(group_label=group,
                                           with_labels=with_labels[k],
                                           render_labels=(legend_enabled and
                                                          not subplots_enabled),
                                           **kwargs)
                    else:
                        # image, landmarks, not masked, not glyph
                        image.view_landmarks(group_label=group,
                                             with_labels=with_labels[k],
                                             render_labels=(legend_enabled and
                                                            not subplots_enabled),
                                             channels=channels, **kwargs)
        else:
            # either there are not any landmark groups selected or they won't
            # be displayed
            if image_is_masked:
                if glyph_enabled or sum_enabled:
                    # image, not landmarks, masked, glyph
                    glyph(image, vectors_block_size=glyph_block_size,
                          use_negative=glyph_use_negative, channels=channels).\
                        view(masked=masked_enabled, **kwargs)
                else:
                    # image, not landmarks, masked, not glyph
                    image.view(masked=masked_enabled, channels=channels,
                               **kwargs)
            else:
                if glyph_enabled or sum_enabled:
                    # image, not landmarks, not masked, glyph
                    glyph(image, vectors_block_size=glyph_block_size,
                          use_negative=glyph_use_negative, channels=channels).\
                        view(**kwargs)
                else:
                    # image, not landmarks, not masked, not glyph
                    image.view(channels=channels, **kwargs)
    else:
        # image won't be displayed
        if landmarks_enabled and len(groups) > 0:
            # there are selected landmark groups and they will be displayed
            if subplots_enabled:
                # calculate subplots structure
                subplots = MatplotlibSubplots()._subplot_layout(len(groups))
            # not image, landmarks
            for k, group in enumerate(groups):
                if subplots_enabled:
                    # create subplot
                    plt.subplot(subplots[0], subplots[1], k + 1)
                    # set axes to equal spacing
                    plt.gca().axis('equal')
                    if legend_enabled:
                        # set subplot's title
                        plt.title(subplots_titles[group])
                    if not axes_visible:
                        # turn axes on/off
                        plt.axis('off')
                    if image_axes_mode:
                        # set axes mode to image
                        plt.gca().invert_yaxis()
                image.landmarks[group].lms.view(image_view=image_axes_mode,
                                                colour_array=groups_colours[group], **kwargs)
            if not subplots_enabled:
                # set axes to equal spacing
                plt.gca().axis('equal')
                if legend_enabled:
                    # display legend on side
                    plt.legend(groups, loc='best')
                if image_axes_mode:
                    # set axes mode to image
                    plt.gca().invert_yaxis()

    # set figure size
    plt.gcf().set_size_inches([x_scale, y_scale] * np.asarray(figure_size))

    # turn axis on/off
    if not axes_visible:
        plt.axis('off')

    # show plot
    plt.show()


def _plot_eigenvalues(model, figure_size, x_scale, y_scale):
    r"""
    Helper function that plots a model's eigenvalues.

    Parameters
    -----------
    model : :map:`PCAModel` or subclass
       The model to be used.

    figure_size : (`int`, `int`)
        The size of the plotted figures.

    x_scale : `float`
        The scale of x axis.

    y_scale : `float`
        The scale of y axis.
    """
    # clear current figure
    clear_output(wait=True)

    # plot eigenvalues ratio
    plt.subplot(211)
    plt.bar(range(len(model.eigenvalues_ratio)),
            model.eigenvalues_ratio)
    plt.ylabel('Variance Ratio')
    plt.xlabel('Component Number')
    plt.title('Variance Ratio per Eigenvector')
    plt.grid("on")

    # plot eigenvalues cumulative ratio
    plt.subplot(212)
    plt.bar(range(len(model.eigenvalues_cumulative_ratio)),
            model.eigenvalues_cumulative_ratio)
    plt.ylim((0., 1.))
    plt.ylabel('Cumulative Variance Ratio')
    plt.xlabel('Component Number')
    plt.title('Cumulative Variance Ratio')
    plt.grid("on")

    # set figure size
    plt.gcf().tight_layout()
    plt.gcf().set_size_inches([x_scale, y_scale] * np.asarray(figure_size))


def _extract_groups_labels(image):
    r"""
    Function that extracts the groups and labels from an image's landmarks.

    Parameters
    ----------
    image : :map:`Image` or subclass
       The input image object.

    Returns
    -------
    group_keys : `list` of `str`
        The list of landmark groups found.

    labels_keys : `list` of `str`
        The list of lists of each landmark group's labels.
    """
    groups_keys = image.landmarks.keys()
    labels_keys = [image.landmarks[g].keys() for g in groups_keys]
    return groups_keys, labels_keys


def _check_n_parameters(n_params, n_levels, max_n_params):
    r"""
    Checks the maximum number of components per level either of the shape
    or the appearance model. It must be None or int or float or a list of
    those containing 1 or {n_levels} elements.
    """
    str_error = ("n_params must be None or 1 <= int <= max_n_params or "
                 "a list of those containing 1 or {} elements").format(n_levels)
    if not isinstance(n_params, list):
        n_params_list = [n_params] * n_levels
    elif len(n_params) == 1:
        n_params_list = [n_params[0]] * n_levels
    elif len(n_params) == n_levels:
        n_params_list = n_params
    else:
        raise ValueError(str_error)
    for i, comp in enumerate(n_params_list):
        if comp is None:
            n_params_list[i] = max_n_params[i]
        else:
            if isinstance(comp, int):
                if comp > max_n_params[i]:
                    n_params_list[i] = max_n_params[i]
            else:
                raise ValueError(str_error)
    return n_params_list
