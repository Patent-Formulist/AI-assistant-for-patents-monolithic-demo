from dataclasses import dataclass


@dataclass
class IdentityPrototype:
    patent_id: int
    analog_id: int
    id: int | None = None
    patent_attribute_id: int | None = None
    general_attribute_id: int | None = None
    analog_attribute_id: int | None = None

    def __post_init__(self):
        """Validate required fields and business rules after initialization."""
        self._validate_ids()
        self._validate_required_fields()
        self._validate_business_rules()

    def _validate_ids(self):
        """Validate that IDs are positive integers if provided."""
        if self.id is not None and self.id <= 0:
            raise ValueError(f"id must be a positive integer, got {self.id}")

        if self.patent_id <= 0:
            raise ValueError(f"patent_id must be a positive integer, got {self.patent_id}")

        if self.analog_id <= 0:
            raise ValueError(f"analog_id must be a positive integer, got {self.analog_id}")

        if self.patent_attribute_id is not None and self.patent_attribute_id <= 0:
            raise ValueError(
                f"patent_attribute_id must be a positive integer, got {self.patent_attribute_id}"
            )

        if self.general_attribute_id is not None and self.general_attribute_id <= 0:
            raise ValueError(
                f"general_attribute_id must be a positive integer, got {self.general_attribute_id}"
            )

        if self.analog_attribute_id is not None and self.analog_attribute_id <= 0:
            raise ValueError(
                f"analog_attribute_id must be a positive integer, got {self.analog_attribute_id}"
            )

    def _validate_required_fields(self):
        """Validate that all required fields are present."""
        # patent_id and analog_id are always required (no default values)
        # general_attribute_id is required (NOT NULL in database)
        if self.general_attribute_id is None:
            raise ValueError("general_attribute_id is required (NOT NULL constraint)")

    def _validate_business_rules(self):
        """Validate business logic rules."""
        # At least one attribute should be specified (patent or analog)
        if self.patent_attribute_id is None and self.analog_attribute_id is None:
            raise ValueError(
                "At least one of patent_attribute_id or analog_attribute_id must be specified"
            )

        # You cannot have identify attribute without any connections
        if (
            self.patent_attribute_id is None
            and self.general_attribute_id is None
            and self.analog_attribute_id is None
        ):
            raise ValueError("At least one attribute must be specified")

    @classmethod
    def create(
        cls,
        patent_id: int,
        analog_id: int,
        general_attribute_id: int,
        patent_attribute_id: int | None = None,
        analog_attribute_id: int | None = None,
        id: int | None = None,
    ) -> "IdentityPrototype":
        """
        Factory method to create a valid IdentityPrototype instance.

        Args:
            patent_id: Patent ID (required)
            analog_id: Analog ID (required)
            general_attribute_id: General attribute ID (required)
            patent_attribute_id: Patent attribute ID (optional)
            analog_attribute_id: Analog attribute ID (optional)
            id: Existing ID for updates (optional)

        Returns:
            Validated IdentityPrototype instance
        """
        return cls(
            patent_id=patent_id,
            analog_id=analog_id,
            general_attribute_id=general_attribute_id,
            patent_attribute_id=patent_attribute_id,
            analog_attribute_id=analog_attribute_id,
            id=id,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "patent_id": self.patent_id,
            "analog_id": self.analog_id,
            "patent_attribute_id": self.patent_attribute_id,
            "general_attribute_id": self.general_attribute_id,
            "analog_attribute_id": self.analog_attribute_id,
        }

    def __repr__(self) -> str:
        return (
            f"IdentityPrototype("
            f"id={self.id}, "
            f"patent_id={self.patent_id}, "
            f"analog_id={self.analog_id}, "
            f"patent_attribute_id={self.patent_attribute_id}, "
            f"general_attribute_id={self.general_attribute_id}, "
            f"analog_attribute_id={self.analog_attribute_id})"
        )
