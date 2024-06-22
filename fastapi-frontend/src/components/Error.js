const handleSelectSummary = async (summaryId) => {
    try {
      const response = await axios.get(`http://localhost:8001/meta_data/${selectedCategory}/${summaryId}`);
      setMetaData(response.data.meta_data);
    } catch (error) {
      console.error('Error fetching meta data:', error);
      // Optionally, set state to indicate an error or display an error message
    }
  };
  