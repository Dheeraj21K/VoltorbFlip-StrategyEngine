import { useEffect } from "react";

type Handler = (key: string) => void;

export function useKeyboard(handler: Handler) {
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      handler(e.key);
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handler]);
}
