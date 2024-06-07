import { Card, CardActions, CardContent, Divider, Typography, Button } from "@mui/material";

export function Result(props) {
    return(
        <Card sx={{marginBottom: "20px"}}>
            <CardContent>
                <Typography>
                    {props.title}
                </Typography>
                <Divider/>
                <Typography>
                    {props.text}
                </Typography>
            </CardContent>
            <CardActions>
                <Button onClick={() => props.addRelevant(props.title)}>Relevant</Button>
                <Button onClick={() => props.addNotRelevant(props.title)}>Not Relevant</Button>
            </CardActions>
        </Card>
    );
}