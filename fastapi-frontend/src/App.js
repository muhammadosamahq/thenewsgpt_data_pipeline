import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ButtonSlider from './components/ButtonSlider';
import SummaryList from './components/SummaryList';
import MetaDataList from './components/MetaDataList';
import StatsTable from './components/StatsTable';

const App = () => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [summaries, setSummaries] = useState([]);
  const [metaData, setMetaData] = useState([]);
  const [stats, setStats] = useState([]);
  const categories = ['business', 'pakistan'];

  useEffect(() => {
    // Load summaries for the selected category
    const fetchSummaries = async () => {
      try {
        const response = await axios.get(`http://localhost:8001/summaries/${selectedCategory}/all`);
        setSummaries(response.data.summaries);
      } catch (error) {
        console.error('Error fetching summaries:', error);
      }
    };

    if (selectedCategory) {
      fetchSummaries();
    }
  }, [selectedCategory]);

  const handleSelectCategory = (category) => {
    setSelectedCategory(category);
    setMetaData([]); // Reset metaData when selecting a new category
    setStats([]); // Reset stats when selecting a new category
  };

  const handleSelectSummary = async (summaryId) => {
    try {
      const response = await axios.get(`http://localhost:8001/meta_data/${selectedCategory}/${summaryId}`);
      setMetaData(response.data.meta_data);
    } catch (error) {
      console.error('Error fetching meta data:', error);
    }
  };

  const handleShowStats = async () => {
    try {
      const response = await axios.get(`http://localhost:8001/stats/${selectedCategory}/all`);
      setStats(response.data.stats);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div className="app">
      <ButtonSlider categories={categories} onSelectCategory={handleSelectCategory} />
      {selectedCategory && (
        <div className="content">
          <SummaryList summaries={summaries} onSelectSummary={handleSelectSummary} />
          {metaData.length > 0 && <MetaDataList metaData={metaData} />}
          <button onClick={handleShowStats}>Show Stats</button>
          {stats.length > 0 && <StatsTable stats={stats} />}
        </div>
      )}
    </div>
  );
};

export default App;

