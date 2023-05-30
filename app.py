from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo 
# required library import
logging.basicConfig(filename="log_file.log" , level=logging.INFO) # loggin basic config
app = Flask(__name__) # flask app config


# flask app routing 
# for main page 
@app.route("/", methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")


# flask app routing 
# for result page 
@app.route("/review" , methods = ['POST' , 'GET'])
@cross_origin()
def index():
    if request.method == 'POST': 
        try:
            product_name = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + product_name
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = product_name + ".txt"
            file_pointer = open(filename, "w")
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": product_name, "Name": name, "Rating": rating, "review_title": commentHead,
                          "Discription": custComment}
                for key, value in mydict.items(): 
                    file_pointer.write('%s:%s\n' % (key, value))
                file_pointer.write("\n \n")
                reviews.append(mydict)
            logging.info("logging final result {}".format(reviews))
            file_pointer.close()

            # mondo db data store 
            client = pymongo.MongoClient("mongodb+srv://rajput89207:<password>@cluster0.q4cidjn.mongodb.net/?retryWrites=true&w=majority")
            db = client['reviews']
            review_col = db['scrap_data']
            review_col.insert_many(reviews)


            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong, try again...'

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0" , debug= True )
