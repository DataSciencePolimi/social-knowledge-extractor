# Social Knowledge Extractor

## Intro

The Social Knowledge Extractor (SKE) is a software tool that allows to discover new entities using Twitter.

## Installation Guide

### From the source code
#### Requirements

* Python (>3.4.0) and pip
* MongoDB
* A [Dandelion](https://dandelion.eu/) Account
* A [Twitter](https://dev.twitter.com/rest/public) Application

#### Setting up the application
Clone the repository:

`git clone https://github.com/DataSciencePolimi/social-knowledge-extractor.git `

Inside the SKE folder initialize a python environment

`virtualenv ske-env`

Activate it

`source ske-env/bin/activate`

The install the requirements

`pip install -r requirements.txt`

#### Setting up the database

The information regarding Dandelion and Twitter are saved in the database.

Thus in order to start to use SKE you need to create in MongoDB a collection named `application_keys` with the documents

    {
      "service" : "dandelion",
      "key_dandelion" : "",
      "app_id" : ""
    }
  
    {
      "service" : "twitter",
      "consumer_key" : "",
      "consumer_secret" : ""
    }

#### Run SKE

To run SKE simply launch

`python app.py `


### Using Docker
#### Requirements

While Docker set up the correct enviroment you still need a [Dandelion](https://dandelion.eu/)  account and a [Twitter](https://dev.twitter.com/rest/public) application in order to run you own istance of SKE.

TBD

## Try the online version

A depolyed version of SKE is available online at [here](http://131.175.141.249/ske/)

A tutorial on how to effectively use it is available [here](https://github.com/DataSciencePolimi/social-knowledge-extractor/wiki/Usage-Guide)
