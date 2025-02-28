import { useState, useEffect } from 'react';
import { 
  Container, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Typography,
  Box,
  TextField
} from '@mui/material';
import axios from 'axios';

// Use the environment variable with a fallback
const API_URL = process.env.REACT_APP_API_URL || 'http://54.172.5.169:8000';

function App() {
  const [products, setProducts] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [recipeFilter, setRecipeFilter] = useState('');

  // Fetch data when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('API URL:', API_URL); // Debug log
        console.log('Attempting to fetch products from:', `${API_URL}/api/v1/products?available_only=true`);
        const productsResponse = await axios.get(`${API_URL}/api/v1/products?available_only=true`);
        setProducts(productsResponse.data);

        console.log('Attempting to fetch recipes from:', `${API_URL}/api/v1/recipes`);
        const recipesResponse = await axios.get(`${API_URL}/api/v1/recipes`);
        console.log('Recipes response:', recipesResponse.data);
        setRecipes(recipesResponse.data);
      } catch (error) {
        console.error('Full error:', error);
        console.error('Error response:', error.response);
        console.error('Error request:', error.request);
      }
    };

    fetchData();
  }, []);

  // Filter recipes when search input changes
  useEffect(() => {
    const fetchFilteredRecipes = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/v1/recipes?product_name=${recipeFilter}`);
        setRecipes(response.data);
      } catch (error) {
        console.error('Error fetching filtered recipes:', error);
      }
    };

    if (recipeFilter) {
      fetchFilteredRecipes();
    }
  }, [recipeFilter]);

  // Format date to local string
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('cs-CZ');
  };

  // Format weight to kg with 3 decimal places
  const formatWeight = (weight) => {
    return `${weight.toFixed(3)} kg`;
  };

  // Format price with currency
  const formatPrice = (price) => {
    return `${price.toFixed(2)} Kč`;
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>

        {/* Products Table */}
        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Products
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell align="right">Current Price</TableCell>
                <TableCell align="right">Original Price</TableCell>
                <TableCell align="right">Discount</TableCell>
                <TableCell align="right">Weight</TableCell>
                <TableCell align="right">Price per kg</TableCell>
                <TableCell>Expiry Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((product) => (
                <TableRow key={product.id}>
                  <TableCell>{product.name}</TableCell>
                  <TableCell align="right">{formatPrice(product.current_price)}</TableCell>
                  <TableCell align="right">{formatPrice(product.original_price)}</TableCell>
                  <TableCell align="right">{`${product.discount}%`}</TableCell>
                  <TableCell align="right">{formatWeight(product.weight)}</TableCell>
                  <TableCell align="right">{formatPrice(product.price_per_kg)}</TableCell>
                  <TableCell>{formatDate(product.expiry_date)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Recipes Table */}
        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Recipes
        </Typography>
        <TextField
          label="Filter Recipes"
          variant="outlined"
          value={recipeFilter}
          onChange={(e) => setRecipeFilter(e.target.value)}
          sx={{ mb: 2 }}
        />
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>English Product</TableCell>
                <TableCell>Recipe Name</TableCell>
                <TableCell align="right">Cooking Time</TableCell>
                <TableCell align="right">Servings</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recipes.map((recipe) => (
                <TableRow key={recipe.id}>
                  <TableCell>{recipe.product}</TableCell>
                  <TableCell>{recipe.product_english}</TableCell>
                  <TableCell>{recipe.recipe_name}</TableCell>
                  <TableCell align="right">{`${recipe.cooking_time} mins`}</TableCell>
                  <TableCell align="right">{recipe.servings}</TableCell>
                  <TableCell>
                    <a href={recipe.recipe_url} target="_blank" rel="noopener noreferrer">
                      View Recipe
                    </a>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
}

export default App;