#!/usr/bin/env python2
""" The design class """

# upconvert.py - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from upconvert.core.design_attributes import DesignAttributes
from upconvert.core.components import Components
from upconvert.core.shape import Point


class Design:
    """ The Design class represents the whole schematic, which is also
    the top level of the output format.  The internal structure of this
    class closely matches the JSON output."""

    def __init__(self):
        self.nets = list()
        self.components = Components()
        self.component_instances = list()
        self.shapes = list()
        self.pins = list()
        self.design_attributes = DesignAttributes()
        self.layout = None
        self.version = dict()
        self.set_version("0.1.0","Upverter converter")


    def bounds(self):
        """ Return the min and max point of a design """
        bounds = [net.bounds() for net in self.nets]
        bounds.extend([anno.bounds() for anno in
                       self.design_attributes.annotations])

        def xform(pt, xo, yo, rot, flip):
            ret = pt
            if flip:
                ret = Point(-ret.x, ret.y)
            # floating pt comparison is a pain
            rot = int(round(rot * 2))
            rot_mtx = [(1,  0, 0,  1), (0,  1, -1, 0),
                       (-1, 0, 0, -1), (0, -1,  1, 0)][rot]
            ret = Point((ret.x * rot_mtx[0] + ret.y * rot_mtx[1]),
                        (ret.x * rot_mtx[2] + ret.y * rot_mtx[3]))
            return Point(ret.x + xo, ret.y + yo)

        for comp in self.component_instances:
            lib_comp = self.components.components[comp.library_id]
            for att, body in zip(comp.symbol_attributes,
                                 lib_comp.symbols[comp.symbol_index].bodies):
                bounds.append([xform(pt, att.x, att.y, att.rotation, att.flip)
                               for pt in body.bounds()])

        bounds.extend([sh.bounds() for sh in self.shapes])

        # flatten out bounds to just a list of Points
        bounds = sum(bounds, [])
        x_values = [pt.x for pt in bounds]
        y_values = [pt.y for pt in bounds]
        # by convention, an empty design will bound just the origin
        if len(x_values) == 0:
            x_values = [0]
            y_values = [0]
        return [Point(min(x_values), min(y_values)),
                Point(max(x_values), max(y_values))]


    def set_version(self, file_version, exporter):
        """ Set the file version and exporter """
        self.version['file_version'] = file_version
        self.version['exporter'] = exporter


    def add_component_instance(self, component_instance):
        """ Add an instance """
        self.component_instances.append(component_instance)


    def add_component(self, library_id, component):
        """ Add a library part """
        self.components.add_component(library_id, component)


    def add_net(self, net):
        """ Add a net """
        self.nets.append(net)

    def add_pin(self, pin):
        """ Add a pin to the schematic sheet """
        self.pins.append(pin)

    def add_shape(self, shape):
        """ Add a shape to the schematic sheet """
        self.shapes.append(shape)

    def set_design_attributes(self, design_attributes):
        """ Add design level attributes """
        self.design_attributes = design_attributes


    def scale(self, factor):
        """ Scale the x & y coordinates in the core. """
        for n in self.nets:
            n.scale(factor)
        self.components.scale(factor)
        for i in self.component_instances:
            i.scale(factor)
        for s in self.shapes:
            s.scale(factor)
        for p in self.pins:
            p.scale(factor)


    def shift(self, dx, dy):
        """ Shift the design dx to all x & dy to all y coordinates in the core. """
        for n in self.nets:
            n.shift(dx, dy)
        self.components.shift(dx, dy)
        for i in self.component_instances:
            i.shift(dx, dy)
        for s in self.shapes:
            s.shift(dx, dy)
        for p in self.pins:
            p.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinates in the core. """
        for n in self.nets:
            n.rebase_y_axis(height)
        self.components.rebase_y_axis(height)
        for i in self.component_instances:
            i.rebase_y_axis(height)
        for s in self.shapes:
            s.rebase_y_axis(height)
        for p in self.pins:
            p.rebase_y_axis(height)


    def generate_netlist(self):
        """ The netlist as generated from the schematic. """
        pass


    def generate_bom(self):
        """ The bill of materials as generated from the schematic. """
        pass


    def json(self):
        """ Return a design as JSON """
        return {
            "version": self.version,
            "nets": [n.json() for n in self.nets],
            "components": self.components.json(),
            "component_instances": [i.json() for i in self.component_instances],
            "shapes": [s.json() for s in self.shapes],
            "pins": [s.json() for s in self.pins],
            "design_attributes": self.design_attributes.json(),
            "layout": self.layout.json() if self.layout is not None else None
            }
