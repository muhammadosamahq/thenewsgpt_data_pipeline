import React, { useState } from 'react';
import axios from 'axios'; // If using axios for API calls

const MyComponent = () => {
  const [data, setData] = useState(null);

  const handleClick = async (category) => {
    try {
      const response = await axios.get(`http://localhost:8001/summaries/${category}/all`);
      setData(response.data.summaries); // Assuming summaries is the key containing data
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div>
      <button onClick={() => handleClick('pakistan')}>Pakistan</button>
      <button onClick={() => handleClick('business')}>Business</button>
      {data && (
        <div>
          <h2>Summaries</h2>
          <ul>
            {Object.keys(data).map((id) => (
              <li key={id}>{data[id]}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MyComponent;
