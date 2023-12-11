import datetime
import numpy as np
import pandas as pd
import pylatex as tex
from pylatex import Tabularx, Package, Center, Table
from pylatex.basic import Environment
from pylatex.base_classes import CommandBase
from itertools import islice

tex.table.COLUMN_LETTERS.update({"R"})


def chunks(data, size):
    it = iter(data)
    for _ in range(0, len(data), size):
        yield {k: data[k] for k in islice(it, size)}


class Landscape(Environment):
    pass


class ReportDocument:
    def __init__(self, name, number, bank):
        self.name = name
        self.number = number
        self.bank = bank

        geometry_options = {
            "tmargin": "35mm",
            "lmargin": "20mm",
            "textwidth": "170mm",
            "textheight": "237mm",
        }

        self.doc = tex.Document(
            f"AccountReport_{self.name}",
            documentclass="article",
            document_options=["10pt", "a4paper"],
            geometry_options=geometry_options,
            lmodern=False,
        )
        self.doc.preamble.append(Package("lscape"))
        self.doc.preamble.append(Package("pdflscape"))
        self.doc.preamble.append(
            tex.NoEscape(r"\renewcommand{\familydefault}{\sfdefault}")
        )
        self.doc.preamble.append(tex.Command("usepackage", "helvet"))
        self.doc.preamble.append(
            tex.Command("usepackage", arguments="placeins", options="section")
        )

        self.doc.preamble.append(
            tex.UnsafeCommand(
                "newcolumntype",
                arguments="R",
                extra_arguments=tex.NoEscape(r">{\raggedleft\arraybackslash}X"),
            )
        )

        self.addHeader()

        self.doc.preamble.append(tex.Command("title", "Financial Report"))
        self.doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))

    def generatePDF(self):
        self.doc.generate_pdf(compiler="pdflatex", clean_tex=False)

    def addHeader(self):
        # Add document header
        header = tex.PageStyle("header", header_thickness=1, footer_thickness=1)
        # Create left header
        with header.create(tex.Head("L")):
            header.append(f"Account name: {self.name}")
            header.append(tex.LineBreak())
            header.append(f"IBAN: {self.number}")

        # Create right header
        with header.create(tex.Head("R")):
            header.append(self.bank)

        # Create left footer
        with header.create(tex.Foot("L")):
            header.append("Econicer - Financial Report")

        # Create right footer
        with header.create(tex.Foot("R")):
            header.append("Page ")
            header.append(tex.Command("thepage"))

        self.doc.preamble.append(header)
        self.doc.change_document_style("header")

    def createFig(self, imagePath, caption, width=tex.NoEscape(r"0.5\linewidth")):
        fig = tex.SubFigure(position="b", width=width)
        fig.add_image(str(imagePath), width=tex.NoEscape(r"\linewidth"))
        fig.add_caption(caption)

        return fig

    def addOverallSection(self, plotPaths):
        """Define plots for the overall section"""

        title = "Overall Financial Report"
        text = "Report for all available years."

        overallPlots = {
            "timeline": "Account saldo total timeline",
            "years": "Yearly income and expenses",
            "pie_income": "Income distribution by category",
            "pie_outgoing": "Expenses distribution by category",
            "hbar_outgoing": "Summation of expenses by category",
            "hbar_incoming": "Summation of incomings by category",
        }

        self.addSection(title, text, overallPlots, plotPaths)
        self.doc.append(tex.Command("newpage"))

    def addSection(self, title, text="", plotDict={}, plotPaths={}):
        with self.doc.create(tex.Section(title)):
            if text:
                self.doc.append(text)

            with self.doc.create(tex.Figure(position="h!")) as fig:
                for i, (plotName, cap) in enumerate(plotDict.items()):
                    subplot = self.createFig(plotPaths[plotName], cap)
                    fig.append(subplot)

                    if (i + 1) % 2 == 0:
                        self.doc.append(tex.LineBreak())

    def addYearlyReports(self, plotPaths, transactions):
        for i, (year, paths) in enumerate(plotPaths.items()):
            self.addYearSection(year, paths, transactions)

            if (i + 1) % 2 == 0:
                self.doc.append(tex.Command("newpage"))

    def addYearSection(self, year, plotPaths, transactions):
        """Define plots for the yearly section"""

        title = f"Financial Report {year}"

        plots = {
            "year": "Monthly income and expenses",
            "categories": "Summation of expenses by category for this year",
        }

        self.addSection(title, plotDict=plots, plotPaths=plotPaths)

        categories = list(set(transactions["groupID"]))

        # add table
        monthTrans = pd.pivot_table(
            transactions,
            index=transactions["date"].dt.strftime("%Y-%m"),
            columns=transactions["groupID"],
            values="value",
            aggfunc=np.sum,
            fill_value=0,
        )
        monthTrans.index = pd.to_datetime(monthTrans.index)
        transInYear = monthTrans[f"{year}-01-01":f"{year}-12-31"]

        header = [""]
        for m in range(1, 13):
            header.append(
                datetime.datetime(day=1, month=m, year=int(year)).strftime(r"%b")
            )
        header.append("Total")

        self.doc.append(tex.Command("scriptsize"))
        tableSpec = "l" + "R" * 13

        with self.doc.create(Landscape()):
            # with self.doc.create(Center()) as centered:
            with self.doc.create(Table(position="h!")) as table:
                # with centered.create(
                table.append(tex.Command("scriptsize"))
                with self.doc.create(
                    Tabularx(tableSpec, width_argument=tex.NoEscape(r"\linewidth"))
                ) as tabular:
                    tabular.add_hline()
                    tabular.add_row(header)
                    tabular.add_hline()
                    for cat in categories:
                        line = []
                        line.append(cat)
                        for m in range(1, 13):
                            value = monthTrans[
                                f"{year}-{m:02d}-01":f"{year}-{m:02d}-02"
                            ]

                            if value.empty:
                                line.append(0)
                                continue
                            value = f"{value[cat].to_list()[0]:.2f}"
                            line.append(value)
                        line.append(f"{np.sum(transInYear[cat]):.2f}")
                        line = [tex.NoEscape(ln) for ln in line]
                        tabular.add_row(line)
                    tabular.add_hline()
                table.add_caption(f"Category overview for year {year}")

    def addFlowSection(self, plotPaths):
        """Define plots for the yearly section"""

        title = "Category Flow"

        plots = {k: f"Spending history of '{k}'" for k in plotPaths.keys()}

        # self.addSection(title, plotDict=plots, plotPaths=plotPaths)
        newpage = False
        with self.doc.create(tex.Section(title)):
            for subset in chunks(plots, 6):
                with self.doc.create(tex.Figure(position="h!")) as fig:
                    for i, (plotName, cap) in enumerate(subset.items()):
                        if newpage:
                            self.doc.append(tex.Command("ContinuedFloat"))
                            newpage = False

                        subplot = self.createFig(plotPaths[plotName], cap)
                        fig.append(subplot)

                        if (i + 1) % 2 == 0:
                            self.doc.append(tex.LineBreak())

                newpage = True

    def addStatisticsSection(self, statistics):
        pass
