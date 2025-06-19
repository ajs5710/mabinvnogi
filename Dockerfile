# probably could have just used pure bash instead of ruby

FROM ruby:3.4.4
RUN apt-get update && apt-get install -y tesseract-ocr
RUN gem install rtesseract

# run this with the folder mounted like so to parse the dyes folders and build a data file
	# docker run --rm -v "$(pwd):/stuff" $(docker build -q .) /stuff/build-data.rb
