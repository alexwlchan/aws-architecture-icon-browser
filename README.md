# aws-architecture-icon-browser

AWS publish the [AWS Architecture Icons][icons], a collection of product and service icons that you can use in architecture diagrams.
I normally download the asset package, which contains PNG and SVG icons.

This is a small web app that lets me look for icons by name, rather than poking through files and folders:

![A screenshot of the browser. There are three headings 'Architecture' 'Category' and 'Resource', and a filter applied for the keyword 'network', which shows a collection of red, orange and purple icons. Icons are shown on the left-hand side, with their name and a list of sizes on the right.](screenshot.png)

I'm sure there are better ways to look at an icon collection if you use professional diagramming software, but I don't have much experience in those tools.
(I use OmniGraffle, but only about 1% of what it can do.)

I made this app

[icons]: https://aws.amazon.com/architecture/icons/



## Features

- Display all the icons in a list
- Show me all the different sizes of icon
- Let me filter for icons by name



## Usage

This tool needs Python 3.
To install and run it:

```
# Clone the repo
git clone https://github.com/alexwlchan/aws-architecture-icon-browser.git
cd aws-architecture-icon-browser

# Install requirements
pip3 install -r requirements.txt

# Run the app
python3 viewer.py
```

The app will automatically download a copy of the AWS Architecture Icons to your computer, then you'll then see the app running at <http://localhost:2520>.

I did consider providing a hosted version, but I'm not sure if anybody else will even find this useful – and there might be copyright issues I don't want to think about right now.



## License

MIT.
