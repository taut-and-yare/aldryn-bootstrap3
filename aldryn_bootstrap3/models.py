# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os
import collections

from functools import partial

import django.forms.models
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.translation import ugettext, ugettext_lazy as _, ungettext

import cms.models
import cms.models.fields
from cms.models.pluginmodel import CMSPlugin

import filer.fields.file
import filer.fields.image
import filer.fields.folder

import djangocms_text_ckeditor.fields
from djangocms_attributes_field.fields import AttributesField

from . import model_fields, constants, utils


"""
CSS - http://getbootstrap.com/css/
Global CSS settings, fundamental HTML elements styled and enhanced with
extensible classes, and an advanced grid system.

The following components marked with "✓" are implemented:

[✓] Grid
[✓] Typography (Blockquote and Cite)
[ ] Code
[✓] Forms (via aldryn-forms)
[✓] Buttons
[✓] Images
[✓] Helper classes (js/ckeditor.js)
[ ] Responsive utilities
"""


"""
CSS - Grid system: "Row" Model
http://getbootstrap.com/css/#grid
"""
@python_2_unicode_compatible
class Bootstrap3RowPlugin(CMSPlugin):
    classes = model_fields.Classes()
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        return str(self.pk)

    def get_short_description(self):
        instance = self.get_plugin_instance()[0]

        if not instance:
            return ugettext('<empty>')

        column_count = len(self.child_plugin_instances or [])
        column_count_str = ungettext(
            '1 column',
            '%(count)i columns',
            column_count
        ) % {'count': column_count}

        if self.classes:
            return '{} ({})'.format(
                self.classes,
                column_count_str
            )
        return column_count_str


"""
CSS - Grid system: "Column" Model
http://getbootstrap.com/css/#grid
"""
@python_2_unicode_compatible
class Bootstrap3ColumnPlugin(CMSPlugin):
    classes = model_fields.Classes()
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )
    tag = models.SlugField(
        verbose_name=_('Tag'),
        default='div',
    )

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        txt = ' '.join([self.get_column_classes(), self.classes])
        if self.tag != 'div':
            txt = '{} ({})'.format(txt, self.tag)
        return txt

    def get_class(self, device, element):
        size = getattr(self, '{}_{}'.format(device, element), None)
        if size is not None:
            if element == 'col':
                return 'col-{}-{}'.format(device, size)
            else:
                return 'col-{}-{}-{}'.format(device, element, size)
        return ''

    def get_column_classes(self):
        classes = []
        for device in constants.DEVICE_SIZES:
            for element in ('col', 'offset', 'push', 'pull'):
                classes.append(self.get_class(device, element))
        return ' '.join(cls for cls in classes if cls)


ColSizeField = partial(
    model_fields.IntegerField,
    null=True,
    blank=True,
    default=None,
    min_value=1,
    max_value=constants.GRID_SIZE,
)

OffsetSizeField = partial(
    model_fields.IntegerField,
    null=True,
    blank=True,
    default=None,
    min_value=0,
    max_value=constants.GRID_SIZE,
)

PushSizeField = partial(
    model_fields.IntegerField,
    null=True,
    blank=True,
    default=None,
    min_value=0,
    max_value=constants.GRID_SIZE,
)

PullSizeField = partial(
    model_fields.IntegerField,
    null=True,
    blank=True,
    default=None,
    min_value=0,
    max_value=constants.GRID_SIZE,
)

for size, name in constants.DEVICE_CHOICES:
    Bootstrap3ColumnPlugin.add_to_class(
        '{}_col'.format(size),
        ColSizeField(verbose_name=_('col-{}-'.format(size))),
    )
    Bootstrap3ColumnPlugin.add_to_class(
        '{}_offset'.format(size),
        OffsetSizeField(verbose_name=_('offset-'.format(size))),
    )
    Bootstrap3ColumnPlugin.add_to_class(
        '{}_push'.format(size),
        PushSizeField(verbose_name=_('push-'.format(size))),
    )
    Bootstrap3ColumnPlugin.add_to_class(
        '{}_pull'.format(size),
        PullSizeField(verbose_name=_('pull-'.format(size))),
    )


"""
CSS - Typography: "Blockquote" Model
http://getbootstrap.com/css/#type-blockquotes
"""
@python_2_unicode_compatible
class Boostrap3BlockquotePlugin(CMSPlugin):
    reverse = models.BooleanField(
        verbose_name=_('Reverse quote'),
        default=False,
        blank=True,
        help_text=_('Reversing the position by adding the Bootstrap 3 '
                    '"blockquote-reverse" class.'),
    )
    classes = model_fields.Classes()
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        if self.reverse:
            return '.blockquote-reverse'
        return ''


"""
CSS - Typography: "Cite" Model
http://getbootstrap.com/css/#type-blockquotes
"""
@python_2_unicode_compatible
class Boostrap3CitePlugin(CMSPlugin):
    classes = model_fields.Classes()
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        return ''


"""
CSS - Buttons: "Button/Link" Model
http://getbootstrap.com/css/#buttons
"""
@python_2_unicode_compatible
class Boostrap3ButtonPlugin(CMSPlugin, model_fields.LinkMixin):
    label = models.CharField(
        verbose_name=_('Display name'),
        blank=True,
        default='',
        max_length=255,
    )
    type = model_fields.LinkOrButton(
        verbose_name='Type',
    )
    # button specific fields
    btn_context = model_fields.Context(
        verbose_name='Context',
        choices=constants.BUTTON_CONTEXT_CHOICES,
        default=constants.BUTTON_CONTEXT_DEFAULT,
    )
    btn_size = model_fields.Size(
        verbose_name='Size',
    )
    btn_block = models.BooleanField(
        verbose_name='Block',
        default=False,
    )
    # text link specific fields
    txt_context = model_fields.Context(
        verbose_name='Context',
        choices=constants.TEXT_LINK_CONTEXT_CHOICES,
        default=constants.TEXT_LINK_CONTEXT_DEFAULT,
        blank=True,
    )
    # common fields
    icon_left = model_fields.Icon(
        verbose_name='Icon left',
    )
    icon_right = model_fields.Icon(
        verbose_name='Icon right',
    )
    classes = model_fields.Classes()

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        return self.label


"""
CSS - Images: Model
http://getbootstrap.com/css/#images
"""
@python_2_unicode_compatible
class Boostrap3ImagePlugin(CMSPlugin):
    file = filer.fields.image.FilerImageField(
        verbose_name=_('Image'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    alt = model_fields.MiniText(
        verbose_name=_('Alternative text'),
        blank=True,
        default='',
    )
    title = model_fields.MiniText(
        verbose_name=_('Title'),
        blank=True,
        default='',
    )
    use_original_image = models.BooleanField(
        verbose_name=_('Use original image'),
        blank=True,
        default=False,
        help_text=_('Outputs the raw image without cropping.')
    )
    override_width = models.IntegerField(
        verbose_name=_('Override width'),
        blank=True,
        null=True,
        help_text=_('The image width as number in pixels. '
                    'Example: "720" and not "720px".'),
    )
    override_height = models.IntegerField(
        verbose_name=_('Override height'),
        blank=True,
        null=True,
        help_text=_('The image height as number in pixels. '
                    'Example: "720" and not "720px".'),
    )
    aspect_ratio = models.CharField(
        verbose_name=_('Aspect ratio'),
        choices=constants.ASPECT_RATIO_CHOICES,
        blank=True,
        default='',
        max_length=10,
        help_text=_('Influences width height of the image '
                    'according to the selected ratio.'),
    )
    shape = models.CharField(
        verbose_name=_('Shape'),
        choices=(
            ('rounded', '.img-rounded'),
            ('circle', '.img-circle'),
        ),
        default='',
        blank=True,
        max_length=64,
    )
    thumbnail = models.BooleanField(
        verbose_name=_('.img-thumbnail'),
        default=False,
        blank=True,
        help_text='Adds the Bootstrap 3 ".img-thumbnail" class.',
    )
    img_responsive = models.BooleanField(
        verbose_name='.img-responsive',
        default=True,
        blank=True,
        help_text='whether to treat the image as using 100% width of the '
                  'parent container (sets the img-responsive class).'
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['alt', 'class'],
    )
    classes = model_fields.Classes()

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        txt = ''
        if self.file_id and self.file.label:
            txt = self.file.label
        return txt

    def srcset(self):
        if not self.file:
            return []
        items = collections.OrderedDict()
        if self.aspect_ratio:
            aspect_width, aspect_height = tuple([int(i) for i in self.aspect_ratio.split('x')])
        else:
            aspect_width, aspect_height = None, None
        for device in constants.DEVICES:
            if self.override_width:
                width = self.override_width
            else:
                # TODO: should this should be based on the containing col size?
                width = device['width_gutter']
            width_tag = str(width)
            if aspect_width is not None and aspect_height is not None:
                height = int(float(width)*float(aspect_height)/float(aspect_width))
                crop = True
            else:
                if self.override_height:
                    height = self.override_height
                else:
                    height = 0
                crop = False
            items[device['identifier']] = {
                'size': (width, height),
                'size_str': '{}x{}'.format(width, height),
                'width_str': '{}w'.format(width),
                'subject_location': self.file.subject_location,
                'upscale': True,
                'crop': crop,
                'aspect_ratio': (aspect_width, aspect_height),
                'width_tag': width_tag,
            }

        return items


"""
Components - http://getbootstrap.com/components/
Over a dozen reusable components built to provide iconography, dropdowns,
input groups, navigation, alerts, and much more.

The following components marked with "✓" are implemented:

[✓] Glyphicons
[ ] Dropdowns
[ ] Button Groups
[ ] Button Dropdowns
[✓] Input Groups (via aldryn-forms)
[✗] Navs (integrate into base.html)
[✗] Navbar (integrate into base.html)
[✗] Breadcrumbs (integrate into base.html)
[✗] Pagination (integrate on addon level)
[✓] Labels
[✗] Badges (integrate on addon level)
[ ] Jumbotron
[✗] Page header (integrate into base.html)
[ ] Thumbnails
[✓] Alerts
[ ] Progress Bars
[ ] Media object
[ ] List Group
[ ] Panels
[ ] Responsive embed
[ ] Wells
"""


"""
Component - Glyphicons: "Icon" Model
http://getbootstrap.com/components/#glyphicons
Component - Font Awesome: "Icon" Model
http://fontawesome.io/
"""
@python_2_unicode_compatible
class Boostrap3IconPlugin(CMSPlugin):
    icon = model_fields.Icon(
        verbose_name=_('Icon'),
        blank=False,
    )
    classes = model_fields.Classes()
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['class'],
    )

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        return self.icon


"""
Component - Label: Model
http://getbootstrap.com/components/#labels
"""
@python_2_unicode_compatible
class Boostrap3LabelPlugin(CMSPlugin):
    label = models.CharField(
        verbose_name=_('Label'),
        blank=True,
        default='',
        max_length=256,
    )
    context = model_fields.Context(
        verbose_name=_('Context'),
        choices=(('default', 'Default',),) + constants.CONTEXT_CHOICES,
        default='default',
        blank=False,
    )
    classes = model_fields.Classes()
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['class'],
    )

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        return self.label


"""
Component - Alert: Model
http://getbootstrap.com/components/#alerts
"""
@python_2_unicode_compatible
class Boostrap3AlertPlugin(CMSPlugin):
    context = model_fields.Context(
        verbose_name=_('Context'),
    )
    icon = model_fields.Icon(
        verbose_name=_('Title icon'),
    )
    classes = model_fields.Classes()
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['class'],
    )

    cmsplugin_ptr = model_fields.CMSPluginField()

    def __str__(self):
        return self.classes




"""
JavaScript Section
[ ] Transitions
[ ] Modal
[ ] Dropdowns
[ ] Scrollspy
[ ] Tab
[ ] Tooltip
[ ] Popover
[ ] Alert
[ ] Button
[ ] Collapse
[ ] Carousel
[ ] Affix
"""


@python_2_unicode_compatible
class Boostrap3WellPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()

    size = model_fields.Size()

    classes = model_fields.Classes()

    def __str__(self):
        return self.classes





@python_2_unicode_compatible
class Boostrap3SpacerPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()

    size = model_fields.Size()

    classes = model_fields.Classes()

    def __str__(self):
        return 'size-' + self.size + ' ' + self.classes


@python_2_unicode_compatible
class Bootstrap3FilePlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()

    file = filer.fields.file.FilerFileField(
        verbose_name=_("file"),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    name = model_fields.MiniText(
        _("name"),
        blank=True,
        default='',
    )
    open_new_window = models.BooleanField(default=False)
    show_file_size = models.BooleanField(default=False)

    # common fields
    icon_left = model_fields.Icon()
    icon_right = model_fields.Icon()

    classes = model_fields.Classes()

    def __str__(self):
        label = self.name
        if not label:
            if self.file_id:
                label = self.file.label
            else:
                label = 'File'
        return label


#########
# Panel #
#########


@python_2_unicode_compatible
class Boostrap3PanelPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()

    context = model_fields.Context(
        choices=constants.PANEL_CONTEXT_CHOICES,
        default=constants.PANEL_CONTEXT_DEFAULT,
        blank=False,
    )

    classes = model_fields.Classes()

    def __str__(self):
        return self.context


@python_2_unicode_compatible
class Boostrap3PanelHeadingPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()

    title = model_fields.MiniText(
        _("title"),
        blank=True,
        default='',
        help_text='Alternatively you can add plugins'
    )

    classes = model_fields.Classes()

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Boostrap3PanelBodyPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()

    classes = model_fields.Classes()

    def __str__(self):
        return self.classes


@python_2_unicode_compatible
class Boostrap3PanelFooterPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()

    classes = model_fields.Classes()

    def __str__(self):
        return self.classes


########
# Grid #
########




#############
# Accordion #
#############

class Bootstrap3AccordionPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()
    index = models.PositiveIntegerField(
        _('index'), null=True, blank=True,
        help_text=_('index of element that should be opened on page load '
                    '(leave it empty if none of the items should be opened)'))
    classes = model_fields.Classes()

    def get_short_description(self):
        instance = self.get_plugin_instance()[0]

        if not instance:
            return ugettext("<Empty>")

        column_count = len(self.child_plugin_instances or [])
        column_count_str = ungettext(
            "1 item",
            "%(count)i items",
            column_count
        ) % {'count': column_count}
        return column_count_str


@python_2_unicode_compatible
class Bootstrap3AccordionItemPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()
    title = model_fields.MiniText(
        _("title"),
        blank=True,
        default='',
    )
    context = model_fields.Context(
        choices=constants.ACCORDION_ITEM_CONTEXT_CHOICES,
        default=constants.ACCORDION_ITEM_CONTEXT_DEFAULT,
        blank=False,
    )

    classes = model_fields.Classes()

    def __str__(self):
        return self.title


#############
# ListGroup #
#############

class Bootstrap3ListGroupPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()
    classes = model_fields.Classes()
    add_list_group_class = models.BooleanField(
        verbose_name='class: list-group',
        default=True,
        blank=True,
        help_text='whether to add the list-group and list-group-item classes'
    )

    def get_short_description(self):
        instance = self.get_plugin_instance()[0]

        if not instance:
            return ugettext("<Empty>")

        column_count = len(self.child_plugin_instances or [])
        column_count_str = ungettext(
            "1 item",
            "%(count)i items",
            column_count
        ) % {'count': column_count}
        return column_count_str


@python_2_unicode_compatible
class Bootstrap3ListGroupItemPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()
    title = model_fields.MiniText(
        _("title"),
        blank=True,
        default='',
    )
    context = model_fields.Context(
        choices=constants.LIST_GROUP_ITEM_CONTEXT_CHOICES,
        default=constants.LIST_GROUP_ITEM_CONTEXT_DEFAULT,
        blank=True,
    )
    state = models.CharField(
        verbose_name='state',
        choices=(
            ('active', 'active'),
            ('disabled', 'disabled'),
        ),
        max_length=255,
        blank=True,
    )

    classes = model_fields.Classes()

    def __str__(self):
        return self.title


############
# Carousel #  derived from https://github.com/aldryn/aldryn-gallery/tree/0.2.6
############

@python_2_unicode_compatible
class Bootstrap3CarouselPlugin(CMSPlugin):
    STYLE_DEFAULT = 'standard'

    STYLE_CHOICES = [
        (STYLE_DEFAULT, _('Standard')),
    ]

    TRANSITION_EFFECT_CHOICES = (
        ('slide', _('Slide')),
    )

    cmsplugin_ptr = model_fields.CMSPluginField()
    style = models.CharField(
        _('Style'),
        choices=STYLE_CHOICES + utils.get_additional_styles(),
        default=STYLE_DEFAULT,
        max_length=50,
    )
    aspect_ratio = models.CharField(
        _("aspect ratio"),
        max_length=10,
        blank=True,
        default='',
        choices=constants.ASPECT_RATIO_CHOICES
    )
    transition_effect = models.CharField(
        _('Transition Effect'),
        choices=TRANSITION_EFFECT_CHOICES,
        default='',
        max_length=50,
        blank=True,
    )
    ride = models.BooleanField(
        _('Ride'),
        default=True,
        help_text=_('Whether to mark the carousel as animating '
                    'starting at page load.'),
    )
    interval = models.IntegerField(
        _('Interval'),
        default=5000,
        help_text=_("The amount of time to delay between automatically "
                    "cycling an item."),
    )
    wrap = models.BooleanField(
        default=True,
        blank=True,
        help_text=_('Whether the carousel should cycle continuously or '
                    'have hard stops.')
    )
    pause = models.BooleanField(
        default=True,
        blank=True,
        help_text=_('Pauses the cycling of the carousel on mouseenter and '
                    'resumes the cycling of the carousel on mouseleave.')
    )
    classes = model_fields.Classes()

    def __str__(self):
        data = django.forms.models.model_to_dict(self)
        data.update(dict(
            style_label=_('Style'),
            transition_effect_label=_('Transition Effect'),
            ride_label=_('Ride'),
            interval_label=_('Interval'),
            aspect_ratio_label=_('Aspect Ratio'),
        ))
        fields = [
            'style',
            'transition_effect',
            'ride',
            'interval',
            'aspect_ratio',
        ]
        if not data['ride']:
            fields.remove('interval')
        return ', '.join([
            '{key}: {value}'.format(
                key=data['{}_label'.format(field)],
                value=data[field]
            ) for field in fields
        ])

    def srcset(self):
        # more or less copied from image plugin.
        # TODO: replace with generic sizes/srcset solution
        items = collections.OrderedDict()
        if self.aspect_ratio:
            aspect_width, aspect_height = tuple([int(i) for i in self.aspect_ratio.split('x')])
        else:
            aspect_width, aspect_height = None, None
        for device in constants.DEVICES:
            width = device['width_gutter']  # TODO: should this should be based on the containing col size?
            width_tag = str(width)
            if aspect_width is not None and aspect_height is not None:
                height = int(float(width)*float(aspect_height)/float(aspect_width))
                crop = True
            else:
                height = 0
                crop = False
            items[device['identifier']] = {
                'size': (width, height),
                'size_str': "{}x{}".format(width, height),
                'width_str': "{}w".format(width),
                # 'subject_location': self.file.subject_location,
                'upscale': True,
                'crop': crop,
                'aspect_ratio': (aspect_width, aspect_height),
                'width_tag': width_tag,
            }

        return items

@python_2_unicode_compatible
class Bootstrap3CarouselSlidePlugin(CMSPlugin, model_fields.LinkMixin):
    excluded_attr_keys = ['class', 'href', 'target', ]
    cmsplugin_ptr = model_fields.CMSPluginField()
    image = filer.fields.image.FilerImageField(
        verbose_name=_('image'),
        blank=False,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    link_text = models.CharField(
        verbose_name=_('link text'),
        max_length=200,
        blank=True
    )
    content = djangocms_text_ckeditor.fields.HTMLField(
        _("Content"),
        blank=True,
        default='',
        help_text=_('alternatively add sub plugins as content'),
    )
    classes = model_fields.Classes()

    def __str__(self):
        image_text = content_text = ''

        if self.image_id:
            if self.image.name:
                image_text = self.image.name
            elif self.image.original_filename \
                    and os.path.split(self.image.original_filename)[1]:
                image_text = os.path.split(self.image.original_filename)[1]
            else:
                image_text = 'Image'
        if self.content:
            text = strip_tags(self.content).strip()
            if len(text) > 100:
                content_text = '{}...'.format(text[:100])
            else:
                content_text = '{}'.format(text)

        if image_text and content_text:
            return '{} ({})'.format(image_text, content_text)
        else:
            return image_text or content_text


@python_2_unicode_compatible
class Bootstrap3CarouselSlideFolderPlugin(CMSPlugin):
    cmsplugin_ptr = model_fields.CMSPluginField()
    folder = filer.fields.folder.FilerFolderField(
        verbose_name=_('folder'),
    )
    classes = model_fields.Classes()

    def __str__(self):
        if self.folder_id:
            return self.folder.pretty_logical_path
        else:
            return _('not selected yet')
