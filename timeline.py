#!/usr/bin/env python3
import cairo
import calendar
import datetime
from dateutil.rrule import rrule, MONTHLY, DAILY
# Examples
TITLE = "Timeline Title"
ANNOTATIONS = ((("Annotation Example 1\nnewline1\nnewline2", 0.5, 0.1),
                ((0.5, 0.15, 0.4, 0.175),)),
               (("Annotation Example 2", 0.3, 0.1), ()))
TASKS = \
    (("Heading 1",
      (("Task\nnewline", "1A", (15, 2)),
       ("Task", "1B", (19, 2), 2, True, 0.05), # duration 2 will be ignored
       ("Task", "1C", (20, 2), 3),
       ("Task", "1D", (23, 2)),
       ("Task", "1E", (23, 2)))),
     ("Heading 2",
      (("Task", "2A", (1, 3), 10),
       ("Task", "2B", (2, 3), 0, True),
       ("Task", "2C", (3, 3)))))
class Annotation:
    def __init__(self, surface, annotations,
                 font="Yanone Kaffeesatz Thin", fontSize=0.015,
                 color=(1, 0, 0), lineWidth=0.001):
        self.context = surface.context()
        self.context.set_source_rgb(*color)
        self.context.select_font_face(font)
        self.context.set_font_size(fontSize)
        self.context.set_line_width(lineWidth)
        for a in annotations:
            for line in a[1]:
                self.draw_line(*line)
        for a in annotations:
            if a[0] != ():
                self.add_text(*a[0])
    def add_text(self, text, x, y0, lineSpacing=1.5):
        xbearing, ybearing, width, height, dx, dy = \
                self.context.text_extents(text)
        y = y0
        for line in  text.splitlines():
            self.context.move_to(x, y)
            self.context.show_text(line)
            y += height * lineSpacing
    def draw_line(self, x0, y0, x1, y1):
        self.context.move_to(x0, y0)
        self.context.line_to(x1, y1)
        self.context.stroke()
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
    def add_title(self, surface, title,
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
    def __init__(self, surface, translation=(0.25, 0.25), scale=0.7):
        self.surface = surface
        self.translation, self.scale = translation, scale
    def _horizontal_line(self, context):
        context.move_to(0, 0)
        context.line_to(1, 0)
        context.stroke()
    def _vertical_steps(self, context, coarseness, timeframe, textSep,
                        tickHeight, start, monthTextSep, tickLabelInterval):
        dt = 1 / float(timeframe.days)
        dx = float(coarseness) * dt
        days = [(t.day, t.month) for t in rrule(DAILY, interval=coarseness,
                                                dtstart=start,
                                                until=(start + timeframe))]
        for i in range(len(days)):
            context.move_to(i * dx, -tickHeight)
            context.line_to(i * dx,  tickHeight)
            context.stroke()
            context.move_to(i * dx, -tickHeight - textSep)
            if i % tickLabelInterval == 0:
                context.show_text(str(days[i][0]))
            context.move_to(i * dx, -tickHeight - textSep - monthTextSep)
            if (i - 1 < 0) or (days[i - 1][1] < days[i][1]):
                context.show_text(calendar.month_abbr[days[i][1]])
        return dict([((t.day, t.month), (t - start).days * dt)
                     for t in rrule(DAILY,
                                    dtstart=start,
                                    until=(start + timeframe))])
    def draw(self, surface, font="Yanone Kaffeesatz Thin", fontSize=0.03,
             lineWidth=0.003, lineColor=(0, 0, 0), textSep=0.01,
             coarseness=2, timeframe=datetime.timedelta(days=45),
             tickHeight=0.01, start=datetime.datetime(2020, 2, 15),
             monthTextSep=0.04, tickLabelInterval=2):
        context = self.context()
        context.select_font_face(font)
        context.set_font_size(fontSize)
        context.set_line_width(lineWidth)
        context.set_source_rgb(*lineColor)

        self._horizontal_line(context)
        return self._vertical_steps(context, coarseness, timeframe, textSep,
                                    tickHeight, start, monthTextSep,
                                    tickLabelInterval)
    def context(self, width=None, height=None):
        context = self.surface.context(width, height, scale=self.scale)
        context.translate(*self.translation)
        return context
class Tasks:
    def __init__(self, timeline, xPositions, heading, vPos=0.05,
                 headingFont="Yanone Kaffeesatz Bold",
                 headingFontSize=0.025):
        self.xPositions = xPositions
        self.context = self._set_heading(timeline.context(),
                                         heading, headingFont,
                                         headingFontSize, vPos)
        self.height = 0.05
    def _set_heading(self, context, heading, headingFont, headingFontSize,
                     vPos, padding=0.03):
        context.set_source_rgb(0, 0, 0)
        context.select_font_face(headingFont)
        context.set_font_size(headingFontSize)
        xbearing, ybearing, width, height, dx, dy = \
                context.text_extents(heading)
        context.translate(0, vPos)
        context.move_to(-width - padding, 0)
        context.show_text(heading)
        return context
    def _set_task_line(self, time, duration, x, y, height, lineWidth,
                       milestone):
        self.context.set_source_rgb(0.8, 0.8, 0.8)
        self.context.set_line_width(lineWidth)
        self.context.move_to(x, 0)
        self.context.line_to(x, y - height)
        self.context.stroke()
        if duration > 0 and not milestone:
            self.context.set_line_width(lineWidth * 5)
            end = datetime.datetime(2020, time[1], time[0]) + \
                  datetime.timedelta(days=duration)
            self.context.move_to(x, y - height - 5 * lineWidth)
            self.context.line_to(self.xPositions[(end.day, end.month)],
                                 y - height - 5 * lineWidth)
            self.context.stroke()
    def _set_task_text(self, text, annotation, x, y0, height, lineSpacing=1.5):
        self.context.set_source_rgb(0, 0, 0)
        y = y0
        for line in  (text + '\n' + annotation).splitlines():
            self.context.move_to(x, y)
            self.context.show_text(line)
            y += height * lineSpacing
    def add_task(self, text, annotation, time, duration=0, milestone=False,
                 vPos=None, vSpacing=0.05, font="Yanone Kaffeesatz Thin",
                 lineWidth=0.001, taskFontSize=0.02, render="lines"):
        self.context.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                                      cairo.FONT_WEIGHT_BOLD if milestone else
                                      cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(taskFontSize * (1.2 if milestone else 1))
        x, y = self.xPositions[time], vPos or self.height
        self.height = y + vSpacing
        xbearing, ybearing, width, height, dx, dy = \
                self.context.text_extents(text)
        if render == "lines":
            self._set_task_line(time, duration, x, y, height, lineWidth,
                                milestone)
        elif render == "text":
            self._set_task_text(text, annotation, x, y, height)
        return self.height
def main(title, annotations, tasks):
    with Surface() as surface:
        surface = surface.add_title(surface, title)
        Annotation(surface, annotations)
        timeline = TimeLine(surface)
        xPositions = timeline.draw(surface)
        for render in ("lines", "text"):
            vPos = 0.05
            for heading in tasks:
                h = Tasks(timeline, xPositions, heading[0], vPos)
                for task in heading[1]:
                    vPos = h.add_task(*task, render=render)
if __name__ == "__main__":
    main(TITLE, ANNOTATIONS, TASKS)
