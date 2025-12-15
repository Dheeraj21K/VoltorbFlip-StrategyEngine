import Board from "./components/Board/Board";
import "./styles/theme.css";

export default function App() {
  return (
    <div style={{ padding: "40px" }}>
      <h1 style={{ color: "white", marginBottom: "20px" }}>
        Voltorb Flip Solver
      </h1>
      <Board />
    </div>
  );
}
