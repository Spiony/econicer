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

    def addOverallSection(self, plotPaths):

        with self.doc.create(tex.Section('Overall Financial Report')):
            self.doc.append('Report for all available data')
            with self.doc.create(tex.Figure(position='h!')):
                with self.doc.create(tex.SubFigure(
                        position='b',
                        width=tex.NoEscape(r'0.5\linewidth'))) as timeLine:

                    timeLine.add_image(
                        str(plotPaths["timeline"]),
                        width=tex.NoEscape(r'\linewidth')
                    )
                    timeLine.add_caption("Account saldo timeline")

                with self.doc.create(tex.SubFigure(
                        position='b',
                        width=tex.NoEscape(r'0.5\linewidth'))) as pie:

                    pie.add_image(
                        str(plotPaths["years"]),
                        width=tex.NoEscape(r'\linewidth')
                    )
                    pie.add_caption('Yearly income and expenses')
                self.doc.append(tex.LineBreak())

                with self.doc.create(tex.SubFigure(
                        position='b',
                        width=tex.NoEscape(r'0.5\linewidth'))) as pie:

                    pie.add_image(
                        str(plotPaths["pie_income"]),
                        width=tex.NoEscape(r'\linewidth')
                    )
                    pie.add_caption('Income distribution by category')

                with self.doc.create(tex.SubFigure(
                        position='b',
                        width=tex.NoEscape(r'0.5\linewidth'))) as pie:

                    pie.add_image(
                        str(plotPaths["pie_outgoing"]),
                        width=tex.NoEscape(r'\linewidth')
                    )
                    pie.add_caption('Expenses distribution by category')

                self.doc.append(tex.LineBreak())

                with self.doc.create(tex.SubFigure(
                        position='b',
                        width=tex.NoEscape(r'0.5\linewidth'))) as pie:

                    pie.add_image(
                        str(plotPaths["categories"]),
                        width=tex.NoEscape(r'\linewidth')
                    )
                    pie.add_caption(
                        "Summation of expenses by category for all years")
        self.doc.append(tex.Command("newpage"))

    def addYearlyReports(self, plotPaths):

        i = 0
        for year, paths in plotPaths.items():
            self.addYearSection(year, paths)

            i += 1
            if (i % 2) == 0:
                self.doc.append(tex.Command("newpage"))

    def addYearSection(self, year, plotPaths):

        with self.doc.create(tex.Section(f'Financial Report {year}')):
            with self.doc.create(tex.Figure(position='h!')):
                with self.doc.create(tex.SubFigure(
                        position='b',
                        width=tex.NoEscape(r'0.5\linewidth'))) as pie:

                    pie.add_image(
                        str(plotPaths["year"]),
                        width=tex.NoEscape(r'\linewidth')
                    )
                    pie.add_caption('Monthly income and expenses')
                with self.doc.create(tex.SubFigure(
                        position='b',
                        width=tex.NoEscape(r'0.5\linewidth'))) as pie:

                    pie.add_image(
                        str(plotPaths["categories"]),
                        width=tex.NoEscape(r'\linewidth')
                    )
                    pie.add_caption(
                        "Summation of expenses by category for this year")
