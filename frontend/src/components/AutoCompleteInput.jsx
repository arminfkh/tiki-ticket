import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";

export default function AutocompleteInput({
  label,
  value,
  options,
  onChange,
  placeholder,
  disabled = false,
  loading = false,
}) {
  const wrapperRef = useRef(null);
  const listboxId = useId();

  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [showAll, setShowAll] = useState(false);

  const filteredOptions = useMemo(() => {
    if (showAll || !value.trim()) {
      return options.slice(0, 12);
    }

    const query = value
      .trim()
      .toLowerCase();

    const startsWithOptions = [];
    const containsOptions = [];

    for (const option of options) {
      const normalizedOption =
        option.toLowerCase();

      if (normalizedOption.startsWith(query)) {
        startsWithOptions.push(option);
      } else if (
        normalizedOption.includes(query)
      ) {
        containsOptions.push(option);
      }
    }

    return [
      ...startsWithOptions,
      ...containsOptions,
    ].slice(0, 12);
  }, [options, value, showAll]);

  useEffect(() => {
    function handleOutsideClick(event) {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target)
      ) {
        setIsOpen(false);
        setShowAll(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener(
      "mousedown",
      handleOutsideClick,
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick,
      );
    };
  }, []);

  function selectOption(option) {
    onChange(option);

    setIsOpen(false);
    setShowAll(false);
    setActiveIndex(-1);
  }

  function handleInputChange(event) {
    onChange(event.target.value);

    setShowAll(false);
    setIsOpen(true);
    setActiveIndex(-1);
  }

  function handleToggle() {
    if (disabled) {
      return;
    }

    setIsOpen((current) => {
      const next = !current;

      setShowAll(next);

      return next;
    });

    setActiveIndex(-1);
  }

  function handleKeyDown(event) {
    if (event.key === "Escape") {
      setIsOpen(false);
      setShowAll(false);
      setActiveIndex(-1);

      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();

      if (!isOpen) {
        setIsOpen(true);
      }

      setActiveIndex((current) => {
        if (filteredOptions.length === 0) {
          return -1;
        }

        return current >=
          filteredOptions.length - 1
          ? 0
          : current + 1;
      });

      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();

      if (!isOpen) {
        setIsOpen(true);
      }

      setActiveIndex((current) => {
        if (filteredOptions.length === 0) {
          return -1;
        }

        return current <= 0
          ? filteredOptions.length - 1
          : current - 1;
      });

      return;
    }

    if (
      event.key === "Enter" &&
      isOpen &&
      filteredOptions.length > 0
    ) {
      event.preventDefault();

      const index =
        activeIndex >= 0
          ? activeIndex
          : 0;

      selectOption(
        filteredOptions[index],
      );
    }
  }

  const showMenu =
    isOpen && !disabled;

  return (
    <label
      className="ticket-filter-field"
      ref={wrapperRef}
    >
      <span>{label}</span>

      <div className="autocomplete">
        <input
          type="text"
          value={value}
          onChange={handleInputChange}
          onFocus={() => {
            if (!disabled) {
              setIsOpen(true);

              if (!value.trim()) {
                setShowAll(true);
              }
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          autoComplete="off"
          role="combobox"
          aria-autocomplete="list"
          aria-expanded={showMenu}
          aria-controls={listboxId}
        />

        <button
          type="button"
          className="autocomplete-toggle"
          onClick={handleToggle}
          disabled={disabled}
          aria-label={`Show ${label.toLowerCase()} options`}
        >
          <span
            className={`autocomplete-arrow ${
              isOpen ? "open" : ""
            }`}
            aria-hidden="true"
          >
            ▾
          </span>
        </button>

        {showMenu && (
          <div
            id={listboxId}
            className="autocomplete-menu"
            role="listbox"
          >
            {loading ? (
              <div className="autocomplete-empty">
                Loading options...
              </div>
            ) : filteredOptions.length > 0 ? (
              filteredOptions.map(
                (option, index) => (
                  <button
                    key={option}
                    type="button"
                    role="option"
                    aria-selected={
                      index === activeIndex
                    }
                    className={`autocomplete-option ${
                      index === activeIndex
                        ? "active"
                        : ""
                    }`}
                    onMouseDown={(event) => {
                      event.preventDefault();
                    }}
                    onMouseEnter={() =>
                      setActiveIndex(index)
                    }
                    onClick={() =>
                      selectOption(option)
                    }
                  >
                    {option}
                  </button>
                ),
              )
            ) : (
              <div className="autocomplete-empty">
                No matches found
              </div>
            )}
          </div>
        )}
      </div>
    </label>
  );
}