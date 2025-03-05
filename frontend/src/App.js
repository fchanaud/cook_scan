import React, { useState } from 'react';
import axios from 'axios';
import {
  Container,
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  IconButton,
  Stack,
  Alert,
  Snackbar,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files).filter(file => 
      file.type.startsWith('image/')
    );
    
    if (files.length === 0) {
      setError('Please select valid image files');
      return;
    }
    
    setSelectedFiles(prev => [...prev, ...files]);
    setError(null);
  };

  const handleRemoveFile = (index) => {
    setSelectedFiles(files => files.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one image');
      return;
    }

    setLoading(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post('http://localhost:8000/analyze-images/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });

      setRecipes(response.data);
      setSelectedFiles([]); // Clear files after successful upload
    } catch (error) {
      console.error('Error uploading images:', error);
      setError(
        error.response?.data?.detail || 
        error.message || 
        'Error analyzing images. Please try again.'
      );
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ 
        my: 4,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 4
      }}>
        {/* Header */}
        <Typography variant="h4" component="h1" align="center">
          CookScan
        </Typography>

        {/* Upload Section */}
        <Box sx={{ width: '100%' }}>
          <Box
            sx={{
              border: '2px dashed #ccc',
              borderRadius: 2,
              p: 3,
              textAlign: 'center',
              bgcolor: 'background.paper',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'primary.main',
              },
            }}
          >
            <input
              accept="image/*"
              type="file"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="image-upload"
            />
            <label htmlFor="image-upload">
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
                <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main' }} />
                <Typography>
                  Drop images here or click to upload
                </Typography>
              </Box>
            </label>
          </Box>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <Stack spacing={1} sx={{ mt: 2 }}>
              {selectedFiles.map((file, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    p: 1,
                    bgcolor: 'background.paper',
                    borderRadius: 1,
                  }}
                >
                  <Typography noWrap sx={{ flex: 1 }}>
                    {file.name}
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => handleRemoveFile(index)}
                    sx={{ color: 'error.main' }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={loading}
                fullWidth
                sx={{ mt: 2 }}
              >
                {loading ? 'Analyzing...' : 'Get Recipes'}
              </Button>
            </Stack>
          )}

          {/* Upload Progress */}
          {loading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                {uploadProgress}% - {uploadProgress === 100 ? 'Processing...' : 'Uploading...'}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Recipe Results */}
        {recipes.length > 0 && (
          <Stack spacing={2} sx={{ width: '100%' }}>
            <Typography variant="h6" align="center">
              Recipe Suggestions
            </Typography>
            {recipes.map((recipe) => (
              <Card key={recipe.id} elevation={0} sx={{ borderRadius: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {recipe.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Ingredients:
                  </Typography>
                  <Box component="ul" sx={{ pl: 2, mt: 0 }}>
                    {recipe.ingredients.map((ingredient, index) => (
                      <Typography component="li" key={index} variant="body2">
                        {ingredient}
                      </Typography>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}

        {/* Error Notification */}
        <Snackbar 
          open={!!error} 
          autoHideDuration={6000} 
          onClose={() => setError(null)}
        >
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
}

export default App; 