def summarize_cell_tracks(df):
    return {
        "cells": int(df["cell_id"].nunique()),
        "time_points": int(df["time"].nunique()),
        "observations": int(len(df)),
    }
