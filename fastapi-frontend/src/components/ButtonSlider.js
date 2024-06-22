import React from 'react';

const ButtonSlider = ({ categories, onSelectCategory }) => {
  return (
    <div className="button-slider">
      {categories.map((category, index) => (
        <button key={index} onClick={() => onSelectCategory(category)}>
          {category}
        </button>
      ))}
    </div>
  );
};

export default ButtonSlider;
