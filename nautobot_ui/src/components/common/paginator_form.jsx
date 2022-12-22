import { Col, Form } from "react-bootstrap";
import React, { useState } from "react";
import { useSearchParams } from 'react-router-dom';


export default function PaginatorForm({ start, end, total_count }) {
  let [searchParams, setSearchParams] = useSearchParams();
  let paginator_string = `Showing ${start} - ${end} of ${total_count}`
  const { setType } = useState("PaginatorForm");

  return (
    <Col sm={3}>
      <Form.Control
        as="select"
        // Default value
        value={searchParams.get("limit")}
        onChange={e => {
          // Set the input value
          setType(e.target.value);
          // Change the query parameters on form change
          setSearchParams({ limit: e.target.value, offset: 0 })
        }}
      >
        <option>50</option>
        <option>100</option>
        <option>200</option>
        <option>500</option>
      </Form.Control>
      <Form.Text muted>
        {paginator_string}
      </Form.Text>
    </Col >
  )
}
