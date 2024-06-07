import * as React from "react";
import { Autocomplete, Box, Button, Divider, FormControl, FormControlLabel, FormLabel, Grid, IconButton, InputAdornment, Pagination, Paper, Radio, RadioGroup, Stack, TextField, Typography } from "@mui/material";
import { Result } from "./result";
import SearchIcon from '@mui/icons-material/Search';
import axios from "axios"
const top100Films = [
  { label: 'The Shawshank Redemption', year: 1994 },
  { label: 'The Godfather', year: 1972 },
  { label: 'The Godfather: Part II', year: 1974 },
  { label: 'The Dark Knight', year: 2008 },
  { label: '12 Angry Men', year: 1957 },
];

function App() {
  const [relevant, setRelevant] = React.useState([]);
  const [irrelevant, setIrrelevant] = React.useState([]);
  const [value, setValue] = React.useState('relevance');
  const [query, setQuery] = React.useState("");
  const [count, setCount] = React.useState(5)
  const [results, setResults] = React.useState([])
  const [page, setPage] = React.useState(1)

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      submit();
    }
  };

  const handleChangeRadio = (event) => {
    setValue(event.target.value);
  };

  const handleChangeQuery = (event) => {
    setQuery(event.target.value)
  }

  const addRelevant = (id) => {
    const new_relevant = relevant.concat([id])
    setRelevant(new_relevant)
    const irrel = irrelevant.filter(it => it !== id)
    setIrrelevant(irrel)
  }

  const addNotRelevant = (id) => {
    const new_relevant = irrelevant.concat([id])
    setIrrelevant(new_relevant)
    const rel = relevant.filter(it => it !== id)
    setRelevant(rel)
  }

  async function rerank() {
    setPage(1)
    const documents = results.map(it => it[0])
    const notrel = documents.filter(it => !relevant.includes(it))
    const request = {
      "query": query,
      "sort_by": value,
      "num_docs": count,
      "relevant": relevant,
      "irrelevant": irrelevant
    }
    const response = (await axios.post('http://127.0.0.1:5000/feedback/', request, { headers: { 'Content-Type': 'application/json' }})).data
    setResults(response)
    
  }

  async function submit() {
    setPage(1)
    const request = {
      "query": query,
      "sort_by": value,
      "num_docs": count
    }
    const response = await (await axios.post('http://127.0.0.1:5000/', request, { headers: { 'Content-Type': 'application/json' }})).data
    setResults(response)
    setRelevant([])
    setIrrelevant([])
  }

  return (
    <div style={{padding: "50px", paddingRight: "250px", paddingLeft: "250px"}}>

    <Grid container spacing={2}>
      <Grid item xs={6} alignItems="center">
        <div style={{display: "flex"}}>
        <TextField sx={{borderRadius: 15, width: "80%"}}
          value={query}
          onChange={handleChangeQuery}
          onKeyDown={handleKeyDown}
          InputLabelProps={{ style: { color: "#9D9D9D" } }}
          InputProps={{
            disableUnderline: true,
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={submit}>
                  <SearchIcon />
                </IconButton>
              </InputAdornment>
            )
          }}  />
          <TextField
          id="standard-number"
          label="Count"
          type="number"
          defaultValue={5}
          value={count}
          onChange={(event) => setCount(event.target.value)}
          sx={{borderRadius: 15, width: "15%", marginLeft: "10px"}}
          InputLabelProps={{
            shrink: true,
          }}
        />
        </div>
      </Grid>

      <Grid item xs={6}>
        <div style={{float: "right"}}>
          <Typography variant="h3">Document Retrieval System</Typography>
        </div>
      </Grid>
      <Grid item xs={12}>
      <FormControl>
      <RadioGroup
        defaultValue="relevance"
        row
        aria-labelledby="demo-row-radio-buttons-group-label"
        name="row-radio-buttons-group"
        value={value}
        onChange={handleChangeRadio}
      >
        <FormControlLabel value="relevance" control={<Radio />} label="Sort by Relevance" />
        <FormControlLabel value="length" control={<Radio />} label="Sort by Length" />
      </RadioGroup>
    </FormControl>
    <Button onClick={rerank} variant="outlined" disabled={relevant.length === 0}>Rerank</Button>

      </Grid>
      <Grid item xs={12}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            {results.slice(5*(page - 1), 5*page).map(
              it => <Result title={it[0]} text={it[1]} addRelevant={addRelevant} addNotRelevant={addNotRelevant}/>
            )}
          </Grid>
        </Grid>
      </Grid>
      <Grid item xs={12}>
        <Stack alignItems="center">{results.length !== 0 ? <Pagination count={results.length / 5} value={page} onChange={handlePageChange}/> : null}</Stack>
        
      </Grid>
    </Grid>
    </div>

);
}

export default App;
