FROM node:16

WORKDIR /app

# Set npm to not require SSL verification
RUN npm config set strict-ssl false

# Copy package files first
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Create production build
RUN npm run build

# Install serve to run the application
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["npm", "start"] 