// import React, { useState } from 'react';
// import axios from 'axios';
// import { useNavigate } from 'react-router-dom';
// import './Login.css';  // Assuming you have a CSS file for styling

// function Login() {
//   const [firstName, setFirstName] = useState('');
//   const [lastName, setLastName] = useState('');
//   const [password, setPassword] = useState('');
//   const navigate = useNavigate();

//   const handleLogin = async (e) => {
//     e.preventDefault();
//     try {
//       const response = await axios.post('http://127.0.0.1:5001/login', {
//         first: firstName,
//         last: lastName,
//         password: password
//       });
//       // Correctly use backticks for template literals
//       navigate(`/patient/${response.data.patient_id}`); // Redirect on successful login
//     } catch (error) {
//       alert(error.response ? error.response.data.message : 'Server error');
//     }
//   };

//   return (
//     <div className="login-page"> {/* This ensures the background and centering */}
//       <div className="login-container">
//         <h2>MedilinkAI Login</h2>
//         <form onSubmit={handleLogin} className="login-form">
//           <input type="text" value={firstName} placeholder="First Name" onChange={e => setFirstName(e.target.value)} />
//           <input type="text" value={lastName} placeholder="Last Name" onChange={e => setLastName(e.target.value)} />
//           <input type="password" value={password} placeholder="Password" onChange={e => setPassword(e.target.value)} />
//           <button type="submit">Login</button>
//           <button onClick={() => navigate('/signup')}>No account? Sign up</button>
//         </form>
//       </div>
//     </div>
//   );
// }  

// export default Login;
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
  const [familyName, setFamilyName] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [identifierValue, setIdentifierValue] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5001/login', {
        family_name: familyName,
        birth_date: birthDate,
        identifier_value: identifierValue
      });
      navigate(`/patient/${response.data.patient_id}`);
    } catch (error) {
      alert(error.response ? error.response.data.message : 'Server error');
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h2>MedilinkAI Login</h2>
        <form onSubmit={handleLogin} className="login-form">
          <input 
            type="text" 
            value={familyName} 
            placeholder="Family Name" 
            onChange={e => setFamilyName(e.target.value)} 
            required
          />
          <input 
            type="text" 
            value={identifierValue} 
            placeholder="Identifier (e.g., MRN)" 
            onChange={e => setIdentifierValue(e.target.value)} 
            required
          />
          <input 
            type="date" 
            value={birthDate} 
            placeholder="Birth Date" 
            onChange={e => setBirthDate(e.target.value)} 
            required
          />
          <button type="submit">Login</button>
          <button type="button" onClick={() => navigate('/signup')}>
            No account? Sign up
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
