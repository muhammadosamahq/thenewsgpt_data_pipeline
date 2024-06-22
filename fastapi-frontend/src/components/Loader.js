const [loading, setLoading] = useState(false);

const fetchSummaries = async () => {
  setLoading(true);
  try {
    const response = await axios.get(`http://localhost:8001/summaries/${selectedCategory}/all`);
    setSummaries(response.data.summaries);
  } catch (error) {
    console.error('Error fetching summaries:', error);
  } finally {
    setLoading(false);
  }
};

// Use the `loading` state to conditionally render loading indicators or placeholders
