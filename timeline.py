#!/usr/bin/env python

import math
import cairo

class Surface:
    def __init__(self, bgcolor=(1, 1, 1), 
                 fname="example", 
                 title="2020 Feb-Mar Timeline",
                 font="Serif",
                 fontSize=0.03,
                 # A3 @ 72 PPI (pixels)
                 width=1191, height=842):
        self.width, self.height = width, height
        self.bgcolor = bgcolor
        self.surface = None
        self.fname = fname
        self.title = title
        self.font, self.fontSize = font, fontSize
    def __enter__(self):
        self.surface = cairo.SVGSurface(self.fname + ".svg", 
                                        self.width, self.height)
        c = self.context(self.width, self.height)
        self.set_background(c)
        self.set_title(c)
        return self
    def set_background(self, context):
        context.set_source_rgb(*self.bgcolor)
        context.paint()
    def set_title(self, context):
        context.set_source_rgb(0, 0, 0)
        context.move_to(0.01, 0.05)
        context.select_font_face(self.font)
        context.set_font_size(self.fontSize)
        context.show_text(self.title)
    def __exit__(self, type, value, tb):
        self.write() 
        self.surface.finish()
    def write(self):
        self.surface.write_to_png(self.fname + ".png")
    def context(self, width, height):
        c = cairo.Context(self.surface)
        c.scale(width, height)
        return c
class Tasks:
    def __init__(self, surface, timeline, heading, vPos=0, 
                 linewidth=0.001, font="Courier New", fontSize=0.02):
        self.xPos = timeline.translate - 0.15
        self.yPos = timeline.translate + vPos
        self.width  = surface.width  * timeline.scale
        self.height = surface.height * timeline.scale
        self.linewidth = linewidth
        self.translate = timeline.translate
        self.font, self.fontSize = font, fontSize
        context = surface.context(surface.width, surface.height)
        self.set_heading(context, heading.upper())
        self.ctx = surface.context(self.width, self.height)
        self.ctx.translate(self.translate, self.translate)  
        self.ctx.select_font_face(self.font)
        self.ctx.set_font_size(0.02)
        self.ctx.set_line_width(self.linewidth)
        textPos = 0.15
        text = "Sample text"
        xbearing, ybearing, width, height, dx, dy = \
                context.text_extents(text)
        self.ctx.move_to(0, 0)
        self.ctx.line_to(0, textPos - height)
        self.ctx.stroke()
        self.ctx.move_to(0, textPos)
        self.ctx.show_text("Sample text")
    def set_heading(self, context, heading):
        context.set_source_rgb(0, 0, 0)
        context.select_font_face(self.font)
        context.set_font_size(self.fontSize)
        xbearing, ybearing, width, height, dx, dy = \
                context.text_extents(heading)
        context.move_to(self.xPos - width, self.yPos)
        context.show_text(heading)
class TimeLine:
    def __init__(self, surface, timeframe=40, coarseness=4,
                 start=15, month=29, font="Serif", scale=0.7,
                 fontSize=0.02, tickHeight=0.01, linewidth=0.003, 
                 translate=0.25, lineColor=(0, 0, 0)):
        self.linewidth = linewidth
        self.lineColor = lineColor
        self.timeframe = timeframe
        self.start, self.month = start, month
        self.translate = 0.25
        self.tickHeight = tickHeight
        self.coarseness = coarseness
        self.scale = scale
        self.width  = surface.width  * scale
        self.height = surface.height * scale

        self.ctx = surface.context(self.width, self.height)
        self.ctx.select_font_face(font)
        self.ctx.set_font_size(fontSize)
        self.ctx.set_line_width(self.linewidth)
        self.ctx.set_source_rgb(*self.lineColor)
        self.ctx.translate(self.translate, self.translate)  
    def draw(self):
        self.horizontal_line()
        self.vertical_steps()
    def horizontal_line(self):
        self.ctx.move_to(0, 0)
        self.ctx.line_to(1, 0) 
        self.ctx.stroke()
    def vertical_steps(self, textSep=0.01):
        dx = float(self.coarseness) / self.timeframe
        for i in range(self.timeframe / self.coarseness + 1):
            self.ctx.move_to(i * dx, -self.tickHeight)
            self.ctx.line_to(i * dx, self.tickHeight)
            self.ctx.stroke()
            self.ctx.move_to(i * dx, -self.tickHeight - textSep)
            self.ctx.show_text(str((self.start + 
                                    i * self.coarseness) % self.month))
def main():
    with Surface() as surface:
        timeline = TimeLine(surface)
        Tasks(surface, timeline, "TEST")
        timeline.draw()
if __name__ == "__main__":
    main()
