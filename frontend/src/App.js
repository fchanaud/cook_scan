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
import CameraAltIcon from '@mui/icons-material/CameraAlt';

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
        timeout: 30000, // 30 second timeout
      });

      setRecipes(response.data);
    } catch (error) {
      console.error('Upload error:', error);
      setError(
        error.response?.data?.detail || 
        'Network error. Please check your connection and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 2 }}>
      <Box sx={{ width: '100%' }}>
        {/* Upload Area */}
        <Box 
          sx={{ 
            p: 2,
            mb: 2,
            border: '2px dashed #ccc',
            borderRadius: 2,
            textAlign: 'center',
            backgroundColor: '#f8f8f8'
          }}
        >
          <input
            type="file"
            accept="image/*"
            multiple
            capture="environment"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            id="image-input"
          />
          <label htmlFor="image-input">
            <Button
              variant="contained"
              component="span"
              startIcon={<CameraAltIcon />}
              fullWidth
              sx={{ mb: 2 }}
            >
              Take Photo
            </Button>
          </label>
          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUploadIcon />}
            fullWidth
          >
            Upload Images
            <input
              type="file"
              accept="image/*"
              multiple
              hidden
              onChange={handleFileSelect}
            />
          </Button>
        </Box>

        {/* Selected Files List */}
        {selectedFiles.length > 0 && (
          <Stack spacing={1} sx={{ mb: 2 }}>
            {selectedFiles.map((file, index) => (
              <Card key={index} variant="outlined">
                <CardContent sx={{ 
                  py: 1, 
                  px: 2, 
                  '&:last-child': { pb: 1 },
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <Typography variant="body2" noWrap>
                    {file.name}
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => handleRemoveFile(index)}
                    sx={{ ml: 1 }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardContent>
              </Card>
            ))}
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={loading}
              fullWidth
              sx={{ mt: 2 }}
            >
              Get Recipes
            </Button>
          </Stack>
        )}

        {/* Loading Progress */}
        {loading && (
          <Box sx={{ width: '100%', mb: 2 }}>
            <LinearProgress variant="determinate" value={uploadProgress} />
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
              {uploadProgress}% - {uploadProgress === 100 ? 'Processing...' : 'Uploading...'}
            </Typography>
          </Box>
        )}

        {/* Recipe Results */}
        {recipes.length > 0 && (
          <Stack spacing={2}>
            <Typography variant="h6" align="center" sx={{ mb: 2 }}>
              Recipe Suggestions
            </Typography>
            {recipes.map((recipe) => (
              <Card 
                key={recipe.id} 
                elevation={2} 
                sx={{ 
                  borderRadius: 2,
                  mb: 2
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontSize: '1.1rem' }}>
                    {recipe.title}
                  </Typography>
                  <Typography 
                    variant="subtitle2" 
                    color="text.secondary" 
                    gutterBottom 
                    sx={{ mt: 2 }}
                  >
                    Ingredients:
                  </Typography>
                  <Box component="ul" sx={{ pl: 2, mt: 0 }}>
                    {recipe.ingredients.map((ingredient, index) => (
                      <Typography 
                        component="li" 
                        key={index} 
                        variant="body2"
                        sx={{ mb: 0.5 }}
                      >
                        {ingredient}
                      </Typography>
                    ))}
                  </Box>
                  {recipe.instructions && (
                    <>
                      <Typography 
                        variant="subtitle2" 
                        color="text.secondary" 
                        sx={{ mt: 2 }}
                      >
                        Instructions:
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {recipe.instructions}
                      </Typography>
                    </>
                  )}
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
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            severity="error" 
            onClose={() => setError(null)}
            sx={{ width: '100%' }}
          >
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
}

export default App; 