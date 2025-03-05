import React, { useState } from 'react';
import axios from 'axios';
import {
  Container,
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
} from '@mui/material';

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileSelect = (event) => {
    setSelectedFiles(Array.from(event.target.files));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/analyze-images/', formData);
      setRecipes(response.data);
    } catch (error) {
      console.error('Error uploading images:', error);
    }
    setLoading(false);
  };

  const handleFavorite = async (recipeId) => {
    try {
      await axios.post(`http://localhost:8000/recipes/favorite/${recipeId}`);
      setRecipes(recipes.map(recipe => 
        recipe.id === recipeId 
          ? { ...recipe, is_favorite: true }
          : recipe
      ));
    } catch (error) {
      console.error('Error marking as favorite:', error);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          CookScan
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Scan your ingredients and discover recipes
        </Typography>

        <input
          accept="image/*"
          type="file"
          multiple
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="image-upload"
        />
        <label htmlFor="image-upload">
          <Button variant="contained" component="span">
            Select Images
          </Button>
        </label>

        {selectedFiles.length > 0 && (
          <>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected {selectedFiles.length} image{selectedFiles.length !== 1 ? 's' : ''}
            </Typography>
            <Button
              variant="contained"
              onClick={handleUpload}
              sx={{ ml: 2 }}
              disabled={loading}
            >
              Upload and Analyze
            </Button>
          </>
        )}

        {loading && <CircularProgress sx={{ mt: 2 }} />}

        <Box sx={{ mt: 4 }}>
          {recipes.map((recipe) => (
            <Card key={recipe.id} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6">{recipe.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Match: {(recipe.match_percentage * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  Ingredients:
                </Typography>
                <ul>
                  {recipe.ingredients.map((ingredient, index) => (
                    <li key={index}>{ingredient}</li>
                  ))}
                </ul>
                <Button
                  variant="outlined"
                  onClick={() => handleFavorite(recipe.id)}
                  disabled={recipe.is_favorite}
                >
                  {recipe.is_favorite ? 'Favorited' : 'Add to Favorites'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Box>
    </Container>
  );
}

export default App; 