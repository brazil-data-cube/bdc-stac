#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Models used for response and requests validation."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from geojson_pydantic.geometries import (
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

from pydantic import BaseModel, Field, validator
from pydantic.fields import PrivateAttr

from stac_pydantic import Collection, Extensions
from stac_pydantic.api.extensions.query import Operator
from stac_pydantic.links import Links
from stac_pydantic.shared import BBox, DATETIME_RFC339

class HTTPError(BaseModel):
    """Generic HTTP error response."""

    code: int
    description: Optional[str]


class Collections(BaseModel):
    """Colletions view response."""

    collections: List[Collection]
    links: Links


class OGCSearch(BaseModel):
    """Base Search for OGC Features."""

    bbox: Optional[BBox]
    datetime: Optional[str]
    limit: int = 10
    page: int = 1

    @property
    def start_date(self) -> Optional[datetime]:
        """Start date property."""
        values = self.datetime.split("/")
        if len(values) == 1:
            return None
        if values[0] == "..":
            return None
        return datetime.strptime(values[0], DATETIME_RFC339)

    @property
    def end_date(self) -> Optional[datetime]:
        """End date property """
        values = self.datetime.split("/")
        if len(values) == 1:
            return datetime.strptime(values[0], DATETIME_RFC339)
        if values[1] == "..":
            return None
        return datetime.strptime(values[1], DATETIME_RFC339)


    @validator("datetime")
    def validate_datetime(cls, v):
        """Validate datetime."""
        if "/" in v:
            values = v.split("/")
        else:
            # Single date is interpreted as end date
            values = ["..", v]

        dates = []
        for value in values:
            if value == "..":
                dates.append(value)
                continue
            try:
                datetime.strptime(value, DATETIME_RFC339)
                dates.append(value)
            except:
                raise ValueError(f"Invalid datetime, must match format ({DATETIME_RFC339}).")

        if ".." not in dates:
            if datetime.strptime(dates[0], DATETIME_RFC339) > datetime.strptime(dates[1], DATETIME_RFC339):
                raise ValueError("Invalid datetime range, must match format (begin_date, end_date)")
        return v

    @validator("bbox", pre=True)
    def validate_bbox(cls, value):
        """Validate bbox."""
        if isinstance(value, str):
            return value.split(",")
        return value


class STACSearchGET(OGCSearch):
    """STAC Search."""

    collections: str
    ids: str

    @validator("bbox")
    def validate_bbox(cls, value):
        """Validate bbox."""
        if isinstance(value, str):
            return value.split(",")
        return value

    @validator("collections", pre=True)
    def validate_collections(cls, value):
        """Validate collections."""
        if isinstance(value, str):
            return value.split(",")
        return value

    @validator("ids", pre=True)
    def validate_ids(cls, value):
        """Validate ids."""
        if isinstance(value, str) and "GET" in cls.method:
            return value.split(",")
        return value


class STACSearchPOST(STACSearchGET):
    """STAC Search."""
    collections: List[str]
    ids: Optional[List[str]]
    intersects: Optional[Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]]
    query: Optional[Dict[str, Dict[Operator, Any]]]

    @validator("bbox")
    def validate_bbox(cls, value):
        """Validate bbox."""
        return value

    @validator("intersects")
    def validate_spatial(cls, v, values):
        """Validate spatial query"""
        if v and values["bbox"]:
            raise ValueError("intersects and bbox parameters are mutually exclusive")
        return v


class TemporalCycle(BaseModel):
    """Temporal Cycle mode."""

    step: int
    unit: str


class TemporalCompostion(BaseModel):
    """Temporal Composition mode."""

    step: str
    unit: str
    _schema: str = Field(alias="schema")
    cycle: Dict[str, TemporalCycle]


class BDCExtension(BaseModel):
    """BDC Extension model."""

    tiles: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    grs: Optional[str]
    type: Optional[str]
    bands_quicklook: Optional[List[str]]
    crs: Optional[str]
    temporal_composition: Optional[str]

    class Config:
        """BDC Extension config."""

        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"bdc:{field_name}"


Extensions.register("bdc", BDCExtension)
