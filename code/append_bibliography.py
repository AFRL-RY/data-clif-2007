'''
    This program will append the bibliography information to the end of the
    html page.  It will look for "<h2>Bibliography</h2>" then anything
    below that line will be replaced by the information in bibligraphy.txt
'''
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bibliography_text_file",
                        help="name of the bibliography_text file",
                        action="store", required=True)
    parser.add_argument("-f", "--file_html",
                        help="name of the html file",
                        action="store", required=True)
    args = parser.parse_args()

    # first lets read the file_html
    new_html_data = []
    with open(args.file_html, 'r') as html_file:
        for html_line in html_file:
            if "<h2>Bibliography</h2>" in html_line:
                new_html_data.append(html_line)
                # ok found the right spot in the file lets break
                break
            else:
                new_html_data.append(html_line)

    # now lets add the bibliographies
    with open(args.bibliography_text_file, 'r') as bib_file:
        new_html_data.append("<ol>\n")
        for bib_line in bib_file:
            first_space = bib_line.find(' ')
            bib_text = bib_line[first_space+1:-1]
            new_html_data.append("<li>%s</li>\n" % bib_text)
        # now append the stuff at the end of the html file
        new_html_data.append('''
</ol>
                
        <!-- Column 1 end -->
    </div>
</div>
<div id="footer">
	<div id="footercontent">
    <a href="index.php?collection=sitemap&page=sitemap">Site Map</a> 
    <a href="mailto:sdms_help@vdl.afrl.af.mil">Contact SDMS</a> 
</div>
<div id="footerAppendage">
    <a href="index.php?collection=notice&page=security">Privacy & Security Notice</a> 
    <a href="index.php?collection=notice&page=hyperlink">External Link Disclaimer</a>
    <a href="index.php?collection=notice&page=contact">Contact Us</a>
    <a href="http://prhome.defense.gov/nofear" title="No Fear Act" target="_new">No Fear Act</a>
    <a href="http://www.usa.gov/" title="USA.gov" target="_new">USA.gov</a>
    
</div>    <div class="publicReviewDate">Current as of 24 February 2017</div>
</div>
</body>
</html>
        ''')
    with open(args.file_html, 'w') as html_file:
        for index in range(0, len(new_html_data)):
            html_file.write(new_html_data[index])
    