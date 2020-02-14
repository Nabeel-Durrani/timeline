#!/usr/bin/env python3
import cairo

class Surface:
    def __init__(self, bgcolor=(1, 1, 1), fname="out",
                 # A3 @ 72 PPI (pixels)
                 width=1191, height=842):
        self.width, self.height = width, height
        self.bgcolor = bgcolor
        self.surface = None
        self.fname = fname
    def __enter__(self):
        self.surface = cairo.SVGSurface(self.fname + ".svg",
                                        self.width, self.height)
        context = self.context()
        context.set_source_rgb(*self.bgcolor)
        context.paint()
        return self
    def __exit__(self, type, value, tb):
        self.write()
        self.surface.finish()
    def write(self):
        self.surface.write_to_png(self.fname + ".png")
    def context(self, width=None, height=None, scale=1):
        context = cairo.Context(self.surface)
        context.scale(scale * (width  or self.width),
                      scale * (height or self.height))
        return context
    def add_title(self, surface, title="Timeline Title",
                  font="Utopia", fontSize=0.04, translation=(0.01, 0.05)):
            context = surface.context()
            context.set_source_rgb(0, 0, 0)
            context.move_to(translation[0], translation[1])
            context.select_font_face(font,
                                     cairo.FONT_SLANT_ITALIC,
                                     cairo.FONT_WEIGHT_BOLD)
            context.set_font_size(fontSize)
            context.show_text(title)
            return self
class TimeLine:
    def __init__(self, surface, timeframe=40, coarseness=4,
                 start=15, month=29, font="Yanone Kaffeesatz Thin", scale=0.7,
                 fontSize=0.03, tickHeight=0.01, linewidth=0.003,
                 lineColor=(0, 0, 0)):
        self.surface = surface
        self.linewidth = linewidth
        self.lineColor = lineColor
        self.timeframe = timeframe
        self.start, self.month = start, month
        self.tickHeight = tickHeight
        self.coarseness = coarseness
        self.scale = scale
        self.font, self.fontSize = font, fontSize
    def draw(self, surface):
        context = self.context()
        context.select_font_face(self.font)
        context.set_font_size(self.fontSize)
        context.set_line_width(self.linewidth)
        context.set_source_rgb(*self.lineColor)

        self._horizontal_line(context)
        self._vertical_steps(context)
    def _horizontal_line(self, context):
        context.move_to(0, 0)
        context.line_to(1, 0)
        context.stroke()
    def _vertical_steps(self, context, textSep=0.01):
        dx = float(self.coarseness) / self.timeframe
        for i in range(int(self.timeframe / self.coarseness) + 1):
            context.move_to(i * dx, -self.tickHeight)
            context.line_to(i * dx,  self.tickHeight)
            context.stroke()
            context.move_to(i * dx, -self.tickHeight - textSep)
            context.show_text(str((self.start +
                                   i * self.coarseness) % self.month))
    def context(self, width=None, height=None, translate=0.25):
        context = self.surface.context(width, height, scale=self.scale)
        context.translate(translate, translate)
        return context
class Tasks:
    def __init__(self, timeline, heading, vPos=0,
                 linewidth=0.001, font="Yanone Kaffeesatz Thin",
                 headingFont="Yanone Kaffeesatz Bold",
                 headingFontSize=0.025, taskFontSize=0.02):
        self.vPos = vPos
        self.linewidth = linewidth
        self.font = font
        self.headingFontSize, self.taskFontSize = headingFontSize, taskFontSize
        self.headingFont = headingFont
        self.set_heading(timeline.context(), heading)
        self.add_task(timeline.context(),
                      "Example text 2")
    def set_heading(self, context, heading, padding=0.03):
        context.set_source_rgb(0, 0, 0)
        context.select_font_face(self.headingFont)
        context.set_font_size(self.headingFontSize)
        xbearing, ybearing, width, height, dx, dy = \
                context.text_extents(heading)
        context.move_to(-width - padding, self.vPos)
        context.show_text(heading)
    def add_task(self, context, text):
        context.select_font_face(self.font)
        context.set_font_size(self.taskFontSize)
        context.set_line_width(self.linewidth)
        textPos = 0.15
        xbearing, ybearing, width, height, dx, dy = \
                context.text_extents(text)
        context.move_to(0, 0)
        context.line_to(0, textPos - height)
        context.stroke()
        context.move_to(0, textPos)
        context.show_text(text)
def main():
    with Surface() as surface:
        timeline = TimeLine(surface.add_title(surface))
        Tasks(timeline, "Example Text 1")
        timeline.draw(surface)

if __name__ == "__main__":
    main()
