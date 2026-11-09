import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the EduPredict login screen with the local demo hint', () => {
  localStorage.clear();
  render(<App />);
  expect(screen.getByRole('heading', { name: 'EduPredict' })).toBeInTheDocument();
  expect(screen.getByText(/Demo account/i)).toBeInTheDocument();
});
