# First stage - build the output
FROM node:16

# create app directory
RUN mkdir /app

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install app dependencies
COPY package.json /app
COPY package-lock.json /app
RUN npm install --silent
RUN npm install react-scripts@3.4.1 -g --silent

# set the backend url environment variable
ARG REACT_APP_BACKEND_URL=
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

# set the frontend url environment variable
ARG REACT_APP_FRONTEND_URL=
ENV REACT_APP_FRONTEND_URL=$REACT_APP_FRONTEND_URL

# set the search endpoint url environment variable
ARG REACT_APP_KGTK_SEARCH_ES_URL='https://kgtk.isi.edu'
ENV REACT_APP_KGTK_SEARCH_ES_URL=$REACT_APP_KGTK_SEARCH_ES_URL

# set the kgtk browser backend environment variable
ARG REACT_APP_USE_KGTK_KYPHER_BACKEND='1'
ENV REACT_APP_USE_KGTK_KYPHER_BACKEND=$REACT_APP_USE_KGTK_KYPHER_BACKEND

# copy the source over
ADD src /app/src
ADD public /app/public

# build app
RUN npm run build

# Second stage - serve it
FROM nginx:latest

COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
