'''
Created on 23 Nov 2015

@author: steph
'''
import datetime
import time
from database import DbUtils
DB = DbUtils()


class MakeGraph():
    def __init__(self):
        #self.createGraph()
        pass

    def createGraph(self, roomName):
        roomSplit = roomName.split('?')
        cleanName = roomSplit[1].replace('%20', ' ')
        graphPeriod = int(roomSplit[2])
        currentTime = time.time() - 86400 * graphPeriod
        tempData = DB.getTemps(cleanName, currentTime)
        boilerData = DB.getAllBoiler()
        pageText = []
        
        pageText.append(self.html_Top())
        pageText.append(self.html_Data(tempData, boilerData))
        pageText.append(self.html_Options(cleanName))
        pageText.append(self.html_Chart())
        pageText.append(self.html_Body())
        
        html_text = ''.join(pageText)
        
        f = open('graph.html', 'w')
        f.write(html_text)
        f.close()


    def html_Top(self):
        html_text = """<html>
            <head>
                <script type="text/javascript" src="https://www.google.com/jsapi"></script>
                <script type="text/javascript">
                    google.load("visualization", "1", {packages:["corechart"]});
                    google.setOnLoadCallback(drawVisualization);
                    """
        return html_text

    def html_Data(self, tempData, boilerData):
        pageText = []
        pageText.append("""function drawVisualization() {
            // Some raw data (not necessarily accurate)
            var data = google.visualization.arrayToDataTable([
                ['Time', 'SetPoint', 'Temperature', 'Outside Temp', 'Boiler',  'Valve %'],
                """)
        lastTemp = 0.0
        for lines in tempData:
            tempTime = lines[2]
            setPoint = lines[3]
            realTemp = float(lines[4])
            valvePos = lines[5] / 10.0
            outsideTemp = lines[6]

            if outsideTemp == None:
                outsideTemp = 0
            
            # Exclude Zero Temperature values
            if realTemp > 0.0:
                lastTemp = realTemp
            if realTemp == 0.0 and lastTemp > 1.0:
                realTemp = 'null'
                
            # Find if boiler is on at temperature time
            for states in reversed(boilerData):
                if tempTime >= states[1]:
                    boilerOn = states[2] * 12
                    break
                
            timeString = (datetime.datetime.fromtimestamp(float(tempTime)).strftime('%d %H:%M'))
            pageText.append("""['{}', {}, {}, {}, {}, {}],
            """.format(timeString,setPoint,realTemp,outsideTemp,boilerOn,valvePos))
        pageText.append("""]);
        """)
        html_text = ''.join(pageText)
        return html_text

    def html_Options(self, roomName):
        html_text = """
        var options = {{
            title : 'Temperature of {}',
            seriesType: 'line',
            interpolateNulls: true,
            series: {{
                3: {{type: 'area'}},
                4: {{type: 'area'}}
            }}
        }};
             """.format(roomName)
        return html_text

    def html_Chart(self):
        html_text = """
        var chart = new google.visualization.ComboChart(document.getElementById('chart_div'));
        chart.draw(data, options);
    }
        </script>
    </head>
            """
        return html_text

    def html_Body(self):
        html_text = """
            <body>
                <div id="chart_div" style="width: 100%; height: 600px;"></div>
                <a href="/index.html"><button type="button">Main UI</button></a>
            </body>
        </html>
            """
        return html_text
