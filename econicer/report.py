import pylatex as tex


class ReportDocument():

    def __init__(self, name, number, bank):
        self.name = name
        self.number = number
        self.bank = bank

        geometry_options = {
            "tmargin": "35mm",
            "lmargin": "25mm",
            "textwidth": "160mm",
            "textheight": "237mm",
        }

        self.doc = tex.Document(
            f"AccountReport_{self.name}",
            documentclass="article",
            document_options=['10pt', "a4paper"],
            geometry_options=geometry_options,
            lmodern=False
        )
        self.doc.preamble.append(tex.NoEscape(
            r"\renewcommand{\familydefault}{\sfdefault}"))
        self.doc.preamble.append(tex.Command('usepackage', 'helvet'))
        self.doc.preamble.append(tex.Command(
            'usepackage', arguments='placeins', options="section"))

        self.addHeader()

        self.doc.preamble.append(tex.Command('title', "Financial Report"))
        # self.doc.preamble.append(Command('bank', 'Anonymous author'))
        self.doc.preamble.append(tex.Command('date', tex.NoEscape(r'\today')))
        # \usepackage[section]{placeins}

    def generatePDF(self):
        self.doc.generate_pdf(compiler="xelatex", clean_tex=False)

    def addHeader(self):
        # Add document header
        header = tex.PageStyle(
            "header", header_thickness=1, footer_thickness=1)
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

    def createFig(self, imagePath, caption, width=tex.NoEscape(r'0.5\linewidth')):
        fig = tex.SubFigure(position='b', width=width)
        fig.add_image(str(imagePath), width=tex.NoEscape(r'\linewidth'))
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

            with self.doc.create(tex.Figure(position='h!')) as fig:

                for i, (plotName, cap) in enumerate(plotDict.items()):

                    subplot = self.createFig(plotPaths[plotName], cap)
                    fig.append(subplot)

                    if (i + 1) % 2 == 0:
                        self.doc.append(tex.LineBreak())

    def addYearlyReports(self, plotPaths):

        for i, (year, paths) in enumerate(plotPaths.items()):
            self.addYearSection(year, paths)

            if (i + 1) % 2 == 0:
                self.doc.append(tex.Command("newpage"))

    def addYearSection(self, year, plotPaths):
        """Define plots for the yearly section"""

        title = f"Financial Report {year}"

        plots = {
            "year": "Monthly income and expenses",
            "categories": "Summation of expenses by category for this year",
        }

        self.addSection(title, plotDict=plots, plotPaths=plotPaths)

    def addStatisticsSection(self, statistics):
        pass
