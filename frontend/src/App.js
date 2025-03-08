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

// Use environment variable or fallback to relative path
const API_URL = process.env.REACT_APP_API_URL || '';

function App() {
  const [products, setProducts] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [recipeFilter, setRecipeFilter] = useState('');

  // Fetch data when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('API URL:', API_URL);
        const productsUrl = `${API_URL}/api/v1/products?available_only=true`;
        console.log('Fetching products from:', productsUrl);
        const productsResponse = await axios.get(productsUrl);
        setProducts(productsResponse.data);

        const recipesUrl = `${API_URL}/api/v1/recipes`;
        console.log('Fetching recipes from:', recipesUrl);
        const recipesResponse = await axios.get(recipesUrl);
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