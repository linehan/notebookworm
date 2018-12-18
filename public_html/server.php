<?php 

class DB extends SQLite3
{
        function __construct($filename)
        {
                $this->open($filename);
        }
}


function array_to_json($array)
{
        $json = json_encode($array, JSON_PRETTY_PRINT|JSON_PARTIAL_OUTPUT_ON_ERROR);

	switch (json_last_error()) {
        case JSON_ERROR_NONE:
                break;
        case JSON_ERROR_DEPTH:
                throw new Exception("[JSON] Maximum stack depth exceeded");
                break;
        case JSON_ERROR_STATE_MISMATCH:
                throw new Exception("[JSON] Underflow or the modes mismatch");
                break;
        case JSON_ERROR_CTRL_CHAR:
                throw new Exception("[JSON] Unexpected control character found");
                break;
        case JSON_ERROR_SYNTAX:
                throw new Exception("[JSON] Syntax error, malformed JSON");
                break;
        case JSON_ERROR_UTF8:
                throw new Exception("[JSON] Malformed UTF-8 characters");
                break;
        default:
                throw new Exception("[JSON] Unknown error");
                break;
    	}

	return $json;
}

function get_search_results($search, $n, $mode, $exact)
{
        $db = new DB("constitutions.db");

        $arr = array();

        $search = SQLite3::escapeString($search);
        $n      = SQLite3::escapeString($n);

        $table = SQLITE3::escapeString("gram_search");

        if ($exact == false) {
                $res = $db->query("
                        SELECT id, text_id, text_year, text_country, freq, n, gram 
                        FROM $table 
                        WHERE gram MATCH '$search'
                        AND n = $n
                        ORDER BY freq DESC
                ");
        } else {
                $res = $db->query("
                        SELECT id, text_id, text_year, text_country, freq, n, gram 
                        FROM $table 
                        WHERE gram = '$search'
                        AND n = $n
                        ORDER BY freq DESC
                ");
        }

        $arr = array();

        while ($row = $res->fetchArray()) {
                $arr[] = array(
                        "id"           => utf8_encode($row[0]),
                        "text_id"      => utf8_encode($row[1]),
                        "text_year"    => utf8_encode($row[2]),
                        "text_country" => utf8_encode($row[3]),
                        "freq"         => utf8_encode($row[4]),
                        "n"            => utf8_encode($row[5]),
                        "gram"         => utf8_encode($row[6])
                );
        }

        return array_to_json(array(
                "search_query"  => $search,
                "total_matches" => count($arr),
                "results"       => $arr
        ));
}

function request($key)
{
        if (isset($_POST[$key])) {
                return $_POST[$key];
        }
        if (isset($_GET[$key])) {
                return $_GET[$key];
        }
        if (!isset($_GET[$key]) && !isset($_POST[$key])) {
                return NULL;
        }
}


try {
        $search  = request("search");
        $n       = request("n");
        $mode    = request("mode");
        $exact   = (request("exact") == "1") ? true : false;
        
        if ($search !== NULL) {
                $output = get_search_results($search, $n, $mode, $exact);
        }

        header("Content-Type: application/json");
        echo $output;
} catch (Exception $e) {
        http_response_code(500);
        echo "[ERR]" . $e->getMessage();
}

?>
